"""Versioned evidence answer flow with explicit per-stage output budgets."""

import argparse
import json
import hashlib
from pathlib import Path
from types import SimpleNamespace

from . import coverage_cli, omission_cli
from .evidence import query_evidence
from .source import FileSourceAdapter, SourceError
from .split_review import review_split
from .evidence_answer_flow import (Dispatch, ProviderFailure, ZaiProvider, _encoded, _profile,
                                   _save, _sha, _task, MAX_SOURCE_BYTES, MAX_CALLS)

SCHEMA = "agora/evidence-answer-flow/v2-experimental"
BUDGET_SCHEMA = "agora/evidence-answer-budgets/v2-experimental"
DEFAULT_BUDGETS = {"schema": BUDGET_SCHEMA, "generation_max_output_tokens": 32768,
                   "support_max_output_tokens": 32768,
                   "relevance_max_output_tokens": 16384,
                   "coverage_max_output_tokens": 8192,
                   "omission_max_output_tokens": 16384}


class ZaiProviderV2(ZaiProvider):
    """Keep the raw receipt when ZAI appends its observed HTML break to JSON."""

    def __call__(self, *args, **kwargs):
        receipt = super().__call__(*args, **kwargs)
        content = receipt.get("content")
        if type(content) is not str:
            return receipt
        try:
            _, end = json.JSONDecoder().raw_decode(content.lstrip())
        except ValueError:
            return receipt
        start = len(content) - len(content.lstrip())
        cutoff = start + end
        if content[cutoff:].strip() != "</br>":
            return receipt
        normalized = content[:cutoff]
        receipt["content_original"] = content
        receipt["content"] = normalized
        receipt["normalization"] = {
            "rule": "trailing_html_break_v1",
            "original_content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "normalized_content_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest()}
        return receipt


def validate_budgets(value):
    if type(value) is not dict or set(value) != set(DEFAULT_BUDGETS) or value.get("schema") != BUDGET_SCHEMA:
        raise ValueError("invalid_budget_profile")
    limits = {"generation_max_output_tokens": (4096, 65536),
              "support_max_output_tokens": (2048, 32768),
              "relevance_max_output_tokens": (2048, 32768),
              "coverage_max_output_tokens": (2048, 16384),
              "omission_max_output_tokens": (4096, 32768)}
    for key, (minimum, maximum) in limits.items():
        if type(value[key]) is not int or not minimum <= value[key] <= maximum:
            raise ValueError("invalid_budget_profile:" + key)
    if sum(value[key] for key in limits) > 131072:
        raise ValueError("total_output_budget_exceeded")
    return value


def run_flow_v2(source, source_id, source_sha256, question, requirements, output,
             provider, *, provider_id="injected", model_requested="glm-5.3-flash",
             diagnose_omissions=True, response_language="es", budgets=None):
    """Create a fresh, private output directory; never retry an uncertain call."""
    task = _task(question, requirements)
    if response_language not in ("es", "en") or type(diagnose_omissions) is not bool:
        raise ValueError("invalid_flow_config")
    if type(provider_id) is not str or not provider_id or type(model_requested) is not str or not model_requested:
        raise ValueError("invalid_provider_config")
    config = _profile(None)
    budgets = validate_budgets(DEFAULT_BUDGETS if budgets is None else budgets)
    output = Path(output)
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    manifest = {"schema": SCHEMA, "status": "rejected", "source_id": source_id,
                "source_sha256": source_sha256, "question": question,
                "requirements": requirements, "task": task,
                "provider_id": provider_id, "model_requested": model_requested,
                "model_effective": "unknown", "source_scope": "supplied_file_only",
                "original_document_completeness": "not_established",
                "adjudication": "not_performed", "memory_admission": "not_performed",
                "disposition": "requires_review", "stages": {}, "dispatches": 0,
                "max_dispatches": MAX_CALLS, "budgets": budgets,
                "budgets_sha256": _sha(_encoded(budgets))}
    dispatch = None
    try:
        adapter = FileSourceAdapter(source, source_id, MAX_SOURCE_BYTES)
        original = adapter._read(source_sha256)
        source_bytes = len(original)
        manifest["source_bytes"] = source_bytes
        manifest["supplied_source_coverage"] = "full"
        dispatch = Dispatch(output, adapter, source_sha256, provider, provider_id, model_requested)
        generation = query_evidence(
            adapter, source_sha256, task, [{"id": "P1", "question": task}],
            lambda system, user: dispatch.call("generation", system, user,
                                               max_output_tokens=budgets["generation_max_output_tokens"],
                                               timeout_seconds=180),
            content_budget=source_bytes, prompt_budget=200000,
            citation_mode="ids", response_language=response_language,
            system_suffix=config["generation_system_suffix"])
        candidate_sha = _save(output / "candidate.json", generation)
        manifest["stages"]["generation"] = {"status": generation["execution_status"],
                                             "sha256": candidate_sha, "path": "candidate.json"}
        if generation["execution_status"] != "complete":
            manifest["status"] = "remote_outcome_unknown" if dispatch.uncertain else "incomplete"
            return manifest
        candidate = generation
        claims = sum(len(p["claims"]) for p in candidate["parts"])
        if claims:
            split = review_split(
                candidate,
                lambda system, user: dispatch.call("support", system, user,
                                                   max_output_tokens=budgets["support_max_output_tokens"],
                                                   timeout_seconds=120),
                lambda system, user: dispatch.call("relevance", system, user,
                                                   max_output_tokens=budgets["relevance_max_output_tokens"],
                                                   timeout_seconds=120))
            split_sha = _save(output / "split-review.json", split)
            manifest["stages"]["claim_review"] = {"status": split["execution_status"],
                                                   "sha256": split_sha,
                                                   "path": "split-review.json"}
            if split["execution_status"] != "complete":
                manifest["status"] = "remote_outcome_unknown" if dispatch.uncertain else "review_incomplete"
                return manifest
        else:
            manifest["stages"]["claim_review"] = {"status": "not_run", "reason": "no_claims"}
        candidate_raw = (output / "candidate.json").read_bytes()
        user = coverage_cli.prepare(original, source_sha256, candidate_raw,
                                    candidate_sha, "P1", task)
        response = dispatch.call("coverage", coverage_cli.SYSTEM, user,
                                 max_output_tokens=budgets["coverage_max_output_tokens"],
                                 timeout_seconds=120)
        coverage = {"schema": coverage_cli.VERSION, "status": "complete",
                    "source_sha256": source_sha256, "candidate_sha256": candidate_sha,
                    "part_id": "P1", "question": task,
                    "coverage": coverage_cli.assess(response), "response": response,
                    "source_completeness": "not_established",
                    "adjudication": "not_performed", "memory_admission": "not_performed",
                    "request_config": {"model": model_requested,
                                       "max_tokens": budgets["coverage_max_output_tokens"],
                                       "timeout_seconds": 120, "retries": 0}}
        coverage_sha = _save(output / "coverage.json", coverage)
        manifest["stages"]["coverage"] = {"status": "complete", "coverage": coverage["coverage"],
                                          "sha256": coverage_sha, "path": "coverage.json"}
        if diagnose_omissions:
            args = SimpleNamespace(source_sha256=source_sha256,
                                   candidate_sha256=candidate_sha, part_id="P1",
                                   question=task, review_sha256=coverage_sha)
            user, units, prior = omission_cli.prepare(
                original, candidate_raw, (output / "coverage.json").read_bytes(), args)
            response = dispatch.call("omission", omission_cli.SYSTEM, user,
                                     max_output_tokens=budgets["omission_max_output_tokens"],
                                     timeout_seconds=120)
            diagnosis_status, findings = omission_cli.validate(response, units)
            disagreement = (prior == "complete" and bool(findings)) or (
                prior == "omitted" and diagnosis_status == "no_omission_found")
            diagnosis = {"schema": "agora/omission-diagnosis/v1-experimental",
                         "status": "complete", "source_sha256": source_sha256,
                         "candidate_sha256": candidate_sha, "review_sha256": coverage_sha,
                         "part_id": "P1", "question": task,
                         "diagnosis_status": diagnosis_status, "omissions": findings,
                         "review_disagreement": disagreement, "response": response,
                         "adjudication": "not_performed", "memory_admission": "not_performed",
                         "source_completeness": "not_established",
                         "request_config": {"model": model_requested,
                                            "max_tokens": budgets["omission_max_output_tokens"],
                                            "timeout_seconds": 120, "retries": 0}}
            diagnosis_sha = _save(output / "omission.json", diagnosis)
            manifest["stages"]["omission"] = {"status": "complete",
                                              "diagnosis_status": diagnosis_status,
                                              "review_disagreement": disagreement,
                                              "sha256": diagnosis_sha, "path": "omission.json"}
        else:
            manifest["stages"]["omission"] = {"status": "not_run", "reason": "not_requested"}
        manifest["status"] = "candidate_reviewed" if (
            manifest["stages"]["claim_review"]["status"] in ("complete", "not_run")
        ) else "review_incomplete"
        if manifest["stages"].get("omission", {}).get("review_disagreement"):
            manifest["status"] = "review_disagreement"
    except (ValueError, SourceError, UnicodeError, OSError) as exc:
        manifest["status"] = ("remote_outcome_unknown" if dispatch and dispatch.uncertain else
                              "incomplete" if dispatch and dispatch.count else "rejected")
        manifest["diagnostic"] = type(exc).__name__
    except ProviderFailure as exc:
        manifest["status"] = "remote_outcome_unknown" if dispatch.uncertain else "incomplete"
        manifest["diagnostic"] = str(exc)
    finally:
        manifest["dispatches"] = dispatch.count if dispatch else 0
        _save(output / "result.json", manifest)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--requirements", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--budgets", type=Path)
    parser.add_argument("--model", default="glm-5.3-flash")
    parser.add_argument("--language", choices=("es", "en"), default="es")
    parser.add_argument("--skip-omissions", action="store_true")
    parser.add_argument("--live-zai", required=True, action="store_true")
    args = parser.parse_args(argv)
    requirements = json.loads(args.requirements.read_text(encoding="utf-8"))
    budgets = json.loads(args.budgets.read_text(encoding="utf-8")) if args.budgets else None
    result = run_flow_v2(args.source, args.source_id, args.source_sha256,
                         args.question, requirements, args.out, ZaiProviderV2(),
                         provider_id="zai", model_requested=args.model,
                         diagnose_omissions=not args.skip_omissions,
                         response_language=args.language, budgets=budgets)
    print(json.dumps({"status": result["status"], "dispatches": result["dispatches"],
                      "output": str(args.out / "result.json")}))
    return 0 if result["status"] in ("candidate_reviewed", "review_disagreement") else 2


if __name__ == "__main__":
    raise SystemExit(main())
