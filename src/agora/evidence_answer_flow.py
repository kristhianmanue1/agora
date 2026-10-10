"""Opt-in, single-source evidence answer flow. All judgments remain advisory."""

import argparse
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import urllib.error
import urllib.request

from . import coverage_cli, omission_cli
from .__main__ import ENDPOINT
from .evidence import query_evidence
from .source import FileSourceAdapter, SourceError
from .split_review import review_split

SCHEMA = "agora/evidence-answer-flow/v1-experimental"
MAX_SOURCE_BYTES = 160000  # coverage_cli's bound; never silently truncate.
MAX_CALLS = 5
PROFILE_SCHEMA = "agora/evidence-answer-flow-profile/v2-experimental"


def _encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _save(path, value):
    """Atomic JSON replacement with file and directory synchronization."""
    path = Path(path)
    raw = _encoded(value)
    temp = path.with_name(path.name + ".tmp")
    fd = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temp.exists():
            temp.unlink()
    return _sha(raw)


class ProviderFailure(RuntimeError):
    pass


class ZaiProvider:
    """One request per call; credentials come from the invoking environment."""

    def __call__(self, system, user, *, model, max_output_tokens, timeout_seconds,
                 json_object):
        key = os.environ.get("ZAI_API_KEY") or os.environ.get("SKOPOS_LLM_API_KEY")
        if not key:
            raise ValueError("provider_key_missing")
        payload = {"model": model, "messages": [
            {"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": max_output_tokens, "temperature": 0}
        if json_object:
            payload["response_format"] = {"type": "json_object"}
        request = urllib.request.Request(
            ENDPOINT, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None

        with urllib.request.build_opener(NoRedirect()).open(request, timeout=timeout_seconds) as response:
            raw = response.read(1048577)
        if len(raw) > 1048576 or key.encode() in raw:
            raise ValueError("invalid_provider_response")
        data = json.loads(raw)
        choice = data["choices"][0]
        receipt = {"content": choice["message"]["content"],
                   "finish_reason": choice.get("finish_reason"),
                   "requested_model": model, "reported_model": data.get("model"),
                   "response_id": data.get("id"), "usage": data.get("usage"),
                   "sent_payload_sha256": _sha(json.dumps(payload).encode())}
        if key in json.dumps(receipt):
            raise ValueError("sensitive_response_rejected")
        return receipt


class ReplayProvider:
    """Return only recorded responses for byte-identical reconstructed requests."""

    def __init__(self, recorded):
        recorded = Path(recorded)
        manifest = json.loads((recorded / "result.json").read_text(encoding="utf-8"))
        if manifest.get("schema") != SCHEMA or manifest.get("status") not in (
                "candidate_reviewed", "review_disagreement"):
            raise ValueError("recorded_flow_not_complete")
        self.manifest = manifest
        self.rows = []
        for ordinal in range(1, manifest["dispatches"] + 1):
            matches = list(recorded.glob(f"{ordinal:02d}-*-attempt.json"))
            if len(matches) != 1:
                raise ValueError("missing_recorded_attempt")
            attempt = json.loads(matches[0].read_text(encoding="utf-8"))
            response_path = recorded / matches[0].name.replace("-attempt.json", "-response.json")
            response = json.loads(response_path.read_text(encoding="utf-8"))
            self.rows.append((attempt, response))
        self.index = 0

    def __call__(self, system, user, *, model, max_output_tokens, timeout_seconds,
                 json_object):
        if self.index >= len(self.rows):
            raise ValueError("replay_exhausted")
        request = {"system": system, "user": user, "model": model,
                   "max_output_tokens": max_output_tokens,
                   "timeout_seconds": timeout_seconds, "temperature": 0,
                   "json_object": json_object}
        attempt, response = self.rows[self.index]
        if (_sha(_encoded(request)) != attempt["request_sha256"] or
                model != attempt["model_requested"] or
                max_output_tokens != attempt["max_output_tokens"] or
                timeout_seconds != attempt["timeout_seconds"]):
            raise ValueError("replay_request_mismatch")
        self.index += 1
        return response


class Dispatch:
    def __init__(self, output, adapter, source_hash, provider, provider_id, model):
        self.output = output
        self.adapter = adapter
        self.source_hash = source_hash
        self.provider = provider
        self.provider_id = provider_id
        self.model = model
        self.count = 0
        self.uncertain = False

    def call(self, stage, system, user, *, max_output_tokens, timeout_seconds):
        if self.count >= MAX_CALLS:
            raise ProviderFailure("call_budget_exhausted")
        # Re-read the pinned source before every possible network effect.
        self.adapter._read(self.source_hash)
        self.count += 1
        request = {"system": system, "user": user, "model": self.model,
                   "max_output_tokens": max_output_tokens,
                   "timeout_seconds": timeout_seconds, "temperature": 0,
                   "json_object": True}
        attempt = {"stage": stage, "ordinal": self.count,
                   "provider_id": self.provider_id, "model_requested": self.model,
                   "source_sha256": self.source_hash, "request_sha256": _sha(_encoded(request)),
                   "max_output_tokens": max_output_tokens,
                   "timeout_seconds": timeout_seconds, "state": "attempted",
                   "remote_outcome": "unknown"}
        prefix = f"{self.count:02d}-{stage}"
        _save(self.output / (prefix + "-attempt.json"), attempt)
        received = False
        try:
            receipt = self.provider(system, user, model=self.model,
                                    max_output_tokens=max_output_tokens,
                                    timeout_seconds=timeout_seconds, json_object=True)
            if type(receipt) is not dict:
                raise ValueError("invalid_provider_receipt")
            _save(self.output / (prefix + "-response.json"), receipt)
            received = True
            if receipt.get("requested_model") != self.model:
                raise ValueError("requested_model_mismatch")
            reported = receipt.get("reported_model")
            if reported is not None and reported != self.model:
                raise ValueError("reported_model_mismatch")
            if type(receipt.get("content")) is not str:
                raise ValueError("invalid_provider_content")
            return receipt
        except Exception as exc:
            # A client error or timeout does not prove the provider did not receive a call.
            http_status = exc.code if isinstance(exc, urllib.error.HTTPError) else None
            remote_outcome = ("received" if received else
                              "http_rejected" if http_status is not None else "unknown")
            self.uncertain |= remote_outcome == "unknown"
            _save(self.output / (prefix + "-outcome.json"),
                  {"state": "failed_local", "diagnostic": type(exc).__name__,
                   "remote_outcome": remote_outcome, "http_status": http_status,
                   "ordinal": self.count})
            raise ProviderFailure(type(exc).__name__) from None


def _task(question, requirements):
    if type(question) is not str or not question.strip() or len(question) > 1600:
        raise ValueError("invalid_question")
    if type(requirements) is not list or not 1 <= len(requirements) <= 12:
        raise ValueError("invalid_requirements")
    if any(type(item) is not str or not item.strip() or len(item) > 200 for item in requirements):
        raise ValueError("invalid_requirements")
    task = question + "\nTask requirements:\n" + "\n".join("- " + x for x in requirements)
    if len(task) > 2000:
        raise ValueError("task_too_long")
    return task


def _profile(profile):
    if profile is None:
        return {"generation_system_suffix": "", "support_max_output_tokens": 2048,
                "relevance_max_output_tokens": 2048}
    if (type(profile) is not dict or set(profile) !=
            {"schema", "id", "generation_system_suffix", "support_max_output_tokens",
             "relevance_max_output_tokens"} or profile["schema"] != PROFILE_SCHEMA or
            type(profile["id"]) is not str or not profile["id"].strip() or
            type(profile["generation_system_suffix"]) is not str or
            len(profile["generation_system_suffix"]) > 1000 or
            profile["support_max_output_tokens"] not in (2048, 4096) or
            profile["relevance_max_output_tokens"] not in (2048, 4096)):
        raise ValueError("invalid_flow_profile")
    return profile


def run_flow(source, source_id, source_sha256, question, requirements, output,
             provider, *, provider_id="injected", model_requested="glm-5.3-flash",
             diagnose_omissions=True, response_language="es", profile=None):
    """Create a fresh, private output directory; never retry an uncertain call."""
    task = _task(question, requirements)
    if response_language not in ("es", "en") or type(diagnose_omissions) is not bool:
        raise ValueError("invalid_flow_config")
    if type(provider_id) is not str or not provider_id or type(model_requested) is not str or not model_requested:
        raise ValueError("invalid_provider_config")
    config = _profile(profile)
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
                "max_dispatches": MAX_CALLS}
    if profile is not None:
        manifest.update(profile=config, profile_sha256=_sha(_encoded(config)))
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
                                               max_output_tokens=4096, timeout_seconds=120),
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
                                                   max_output_tokens=config["support_max_output_tokens"],
                                                   timeout_seconds=120),
                lambda system, user: dispatch.call("relevance", system, user,
                                                   max_output_tokens=config["relevance_max_output_tokens"],
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
                                 max_output_tokens=2048, timeout_seconds=90)
        coverage = {"schema": coverage_cli.VERSION, "status": "complete",
                    "source_sha256": source_sha256, "candidate_sha256": candidate_sha,
                    "part_id": "P1", "question": task,
                    "coverage": coverage_cli.assess(response), "response": response,
                    "source_completeness": "not_established",
                    "adjudication": "not_performed", "memory_admission": "not_performed",
                    "request_config": {"model": model_requested, "max_tokens": 2048,
                                       "timeout_seconds": 90, "retries": 0}}
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
                                     max_output_tokens=4096, timeout_seconds=90)
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
                         "request_config": {"model": model_requested, "max_tokens": 4096,
                                            "timeout_seconds": 90, "retries": 0}}
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


def replay_flow(recorded, source, output):
    replay = ReplayProvider(recorded)
    previous = replay.manifest
    result = run_flow(source, previous["source_id"], previous["source_sha256"],
                      previous["question"], previous["requirements"], output,
                      replay, provider_id="replay", model_requested=previous["model_requested"],
                      diagnose_omissions=previous["stages"]["omission"]["status"] != "not_run",
                      response_language=json.loads((Path(recorded) / "candidate.json").read_text())[
                          "response_language"], profile=previous.get("profile"))
    if replay.index != len(replay.rows) or result["stages"] != previous["stages"]:
        raise ValueError("replay_result_mismatch")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "out"):
        parser.add_argument("--" + name, required=True)
    for name in ("source-id", "source-sha256", "question", "requirements"):
        parser.add_argument("--" + name)
    parser.add_argument("--model", default="glm-5.3-flash")
    parser.add_argument("--language", choices=("es", "en"), default="es")
    parser.add_argument("--skip-omissions", action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live-zai", action="store_true")
    mode.add_argument("--replay-run", type=Path)
    args = parser.parse_args(argv)
    if args.replay_run:
        if any(getattr(args, name) is not None for name in
               ("source_id", "source_sha256", "question", "requirements")):
            parser.error("replay derives task inputs from the recorded run")
        result = replay_flow(args.replay_run, args.source, args.out)
    else:
        if any(getattr(args, name) is None for name in
               ("source_id", "source_sha256", "question", "requirements")):
            parser.error("live flow requires source id, SHA, question and requirements")
        requirements = json.loads(Path(args.requirements).read_text(encoding="utf-8"))
        result = run_flow(args.source, args.source_id, args.source_sha256,
                          args.question, requirements, args.out, ZaiProvider(),
                          provider_id="zai", model_requested=args.model,
                          diagnose_omissions=not args.skip_omissions,
                          response_language=args.language)
    print(json.dumps({"status": result["status"], "dispatches": result["dispatches"],
                      "output": str(Path(args.out) / "result.json")}))
    return 0 if result["status"] in ("candidate_reviewed", "review_disagreement") else 2


if __name__ == "__main__":
    raise SystemExit(main())
