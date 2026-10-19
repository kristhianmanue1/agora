#!/usr/bin/env python3
"""Frozen offline quality battery for the evidence answer flow (v1).

Five scenarios (S2, S5, S6, S7, S8) run against the real product modules with
a simulated provider. Zero network, zero live models. The simulated judgments
verify state vocabulary, axis separation, provenance and uncertainty handling
only -- not semantic quality.
"""
import hashlib
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from agora.evidence_answer_flow import run_flow  # noqa: E402
from agora.source import SourceError, digest  # noqa: E402
from agora.source_evidence_exchange import (  # noqa: E402
    CANDIDATE, EXCHANGE, resolve,
)

BATTERY = "agora/quality-battery/v1"
SOURCE_TEXT = "Atlas scored 91%."


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    return sha_bytes(Path(path).read_bytes())


def canonical(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


class SimulatedProvider:
    """Same call contract and stage detection as the product test suite."""

    def __init__(self, *, fail_stage=None, abstain=False, support="supported"):
        self.calls = []
        self.fail_stage = fail_stage
        self.abstain = abstain
        self.support = support

    def __call__(self, system, user, *, model, max_output_tokens,
                 timeout_seconds, json_object):
        payload = json.loads(user)
        if "evidence_units" in payload and "aspects" in payload:
            stage = "generation"
        elif "Assess each self-contained claim" in system:
            stage = "support"
        elif "Assess whether each claim" in system:
            stage = "relevance"
        elif "Criteria:" in system:
            stage = "coverage"
        else:
            stage = "omission"
        self.calls.append(stage)
        if stage == self.fail_stage:
            raise TimeoutError("simulated timeout")
        if stage == "generation":
            evidence_id = payload["evidence_units"][0]["id"]
            part = {"id": "P1",
                    "status": "not_in_passages" if self.abstain else "answered",
                    "claims": [] if self.abstain else [
                        {"text": "Atlas scored 91%.",
                         "evidence_ids": [evidence_id]}],
                    "missing": ["Answer unavailable."] if self.abstain else []}
            value = {"parts": [part]}
        elif stage == "support":
            value = {"claims": [{"id": 0, "support": self.support,
                                 "quote_indices": [0] if self.support != "insufficient" else [],
                                 "reason": "Exact quote." if self.support != "insufficient"
                                           else "Quote is literal but does not entail the claim."}]}
        elif stage == "relevance":
            value = {"claims": [{"id": 0, "relevance": "relevant",
                                 "reason": "Answers the task."}]}
        elif stage == "coverage":
            value = {"coverage": "complete"}
        else:
            value = {"status": "no_omission_found", "omissions": []}
        return {"content": json.dumps(value), "finish_reason": "stop",
                "requested_model": model, "reported_model": model,
                "usage": {"total_tokens": 7}}


def check(name, expected, observed):
    return {"name": name, "expected": repr(expected), "observed": repr(observed),
            "pass": observed == expected}


def scenario_absent_mandatory(root):
    """S2: mandatory information absent -> declared, never invented."""
    source = root / "s2-source.txt"
    source.write_text(SOURCE_TEXT, encoding="utf-8")
    out = root / "s2-run"
    provider = SimulatedProvider(abstain=True)
    result = run_flow(source, "qb-s2", sha_file(source),
                      "What was the Atlas score and the approved budget?",
                      ["Give the Atlas score.", "Give the approved budget."],
                      out, provider)
    candidate = json.loads((out / "candidate.json").read_text(encoding="utf-8"))
    part = candidate["parts"][0]
    claim_review = result["stages"]["claim_review"]
    return {
        "id": "S2", "name": "absent_mandatory_declared_not_invented",
        "checks": [
            check("flow_status", "candidate_reviewed", result["status"]),
            check("no_invented_claims", 0, len(part["claims"])),
            check("missing_visible", True, len(part["missing"]) > 0),
            check("part_status", "not_in_passages", part["status"]),
            check("claim_review_not_run", ("not_run", "no_claims"),
                  (claim_review["status"], claim_review.get("reason"))),
            check("memory_admission", "not_performed", result["memory_admission"]),
        ]}


def scenario_quote_not_backing(root):
    """S5: literal, resolvable reference coexists with insufficient support."""
    source = root / "s5-source.txt"
    source.write_text(SOURCE_TEXT, encoding="utf-8")
    out = root / "s5-run"
    provider = SimulatedProvider(support="insufficient")
    result = run_flow(source, "qb-s5", sha_file(source),
                      "What was the Atlas score?", ["Give the Atlas score."],
                      out, provider)
    candidate = json.loads((out / "candidate.json").read_text(encoding="utf-8"))
    claim = candidate["parts"][0]["claims"][0]
    unit_ids = {unit["id"] for unit in candidate["evidence_units"]}
    references_resolve = bool(claim["evidence_ids"]) and set(claim["evidence_ids"]) <= unit_ids
    split = json.loads((out / "split-review.json").read_text(encoding="utf-8"))
    rows = split.get("assessment") or []
    support_label = rows[0].get("support") if rows else None
    return {
        "id": "S5", "name": "reference_validity_is_not_semantic_backing",
        "checks": [
            check("references_resolve", True, references_resolve),
            check("support_axis", "insufficient", support_label),
            check("review_flags_revision", "needs_revision", split.get("recommendation")),
            check("adjudication_not_performed", "not_performed", result["adjudication"]),
            check("disposition", "requires_review", result["disposition"]),
            check("completeness_not_established", "not_established",
                  result["original_document_completeness"]),
        ]}


def scenario_altered_source(root):
    """S6: source mutated after fixing its revision -> rejected, zero dispatches."""
    source = root / "s6-source.txt"
    source.write_text(SOURCE_TEXT, encoding="utf-8")
    fixed = sha_file(source)
    source.write_text("Atlas scored 92%.", encoding="utf-8")  # mutation after fixing
    out = root / "s6-run"
    provider = SimulatedProvider()
    result = run_flow(source, "qb-s6", fixed,
                      "What was the Atlas score?", ["Give the Atlas score."],
                      out, provider)
    return {
        "id": "S6", "name": "altered_source_rejected_before_dispatch",
        "checks": [
            check("flow_status", "rejected", result["status"]),
            check("diagnostic", "SourceError", result.get("diagnostic")),
            check("zero_dispatches", 0, result["dispatches"]),
            check("zero_provider_calls", 0, len(provider.calls)),
        ]}


def scenario_partial_derivative(root):
    """S7: derivative of a partial extraction never masquerades as complete."""
    original = root / "s7-original.txt"
    original.write_text("ORIGINAL-BYTES-PLACEHOLDER", encoding="utf-8")
    head, gap, tail = "Alpha results.", "[illegible marginal note]", "Omega closing."
    # The exchange contract requires start_byte >= 1, so byte zero stays outside
    # every segment; a one-byte prefix keeps the fixtures honest about that.
    derived_text = "\n" + head + gap + tail
    derived = root / "s7-derived.txt"
    derived.write_text(derived_text, encoding="utf-8")
    head_bytes = head.encode("utf-8")
    gap_bytes = gap.encode("utf-8")
    manifest = {
        "schema": EXCHANGE,
        "source": {"id": "qb-s7-original", "sha256": sha_file(original),
                   "media_type": "text/plain", "revision": "r1", "uri": None},
        "derivative": {"id": "qb-s7-derived", "sha256": sha_file(derived),
                       "coverage": "partial",
                       "producer": {"system": "quality-battery", "version": "1",
                                    "manifest_sha256": None, "derivation_id": "qb-s7"}},
        "segments": [
            {"id": "seg-1", "start_byte": 1, "end_byte": 1 + len(head_bytes),
             "sha256": sha_bytes(head_bytes),
             "locator": {"kind": "text_range", "value": {"section": "results"}},
             "modality": "text", "extraction_status": "unreviewed"},
            {"id": "seg-2",
             "start_byte": 1 + len(head_bytes) + len(gap_bytes),
             "end_byte": 1 + len(head_bytes) + len(gap_bytes) + len(tail.encode("utf-8")),
             "sha256": sha_bytes(tail.encode("utf-8")),
             "locator": {"kind": "text_range", "value": {"section": "closing"}},
             "modality": "text", "extraction_status": "unreviewed"},
        ],
    }
    raw = canonical(manifest)
    base = {"schema": CANDIDATE, "manifest_sha256": sha_bytes(raw),
            "source_sha256": manifest["source"]["sha256"],
            "derivative_sha256": manifest["derivative"]["sha256"]}
    valid = dict(base, claims=[{
        "id": "c1", "kind": "interpretation_candidate",
        "text": "Alpha results reported.",
        "evidence_refs": [{"segment_id": "seg-1", "start_byte": 1, "end_byte": 6}]}])
    resolution = resolve(derived, raw, manifest, valid, original_path=original)
    gap_claim = dict(base, claims=[{
        "id": "c1", "kind": "interpretation_candidate",
        "text": "Marginal note cited as evidence.",
        "evidence_refs": [{"segment_id": "seg-1",
                           "start_byte": 1 + len(head_bytes),
                           "end_byte": 1 + len(head_bytes) + 5}]}])
    gap_error = None
    try:
        resolve(derived, raw, manifest, gap_claim, original_path=original)
    except SourceError as exc:
        gap_error = str(exc)
    evidence = resolution["claims"][0]["evidence"][0]
    return {
        "id": "S7", "name": "partial_derivative_gap_not_citable",
        "checks": [
            check("coverage_declared_partial", "partial",
                  resolution["derivative"]["coverage"]),
            check("gap_citation_rejected", "evidence_outside_segment", gap_error),
            check("literal_is_source_bytes", "Alpha", evidence["literal_text"]),
            check("semantic_support", "not_verified",
                  resolution["claims"][0]["semantic_support"]),
            check("not_admitted", False, resolution["admitted"]),
            check("original_integrity", "sha256_verified",
                  resolution["original_integrity"]),
        ]}


def scenario_uncertain_remote(root):
    """S8: timeout leaves a durable receipt, unknown outcome, no retries."""
    source = root / "s8-source.txt"
    source.write_text(SOURCE_TEXT, encoding="utf-8")
    out = root / "s8-run"
    provider = SimulatedProvider(fail_stage="support")
    result = run_flow(source, "qb-s8", sha_file(source),
                      "What was the Atlas score?", ["Give the Atlas score."],
                      out, provider)
    attempts = sorted(out.glob("*-attempt.json"))
    support_response = out / "02-support-response.json"
    return {
        "id": "S8", "name": "uncertain_remote_durable_no_retry",
        "checks": [
            check("flow_status", "remote_outcome_unknown", result["status"]),
            check("calls_without_retry", ["generation", "support"], provider.calls),
            check("dispatches_count", 2, result["dispatches"]),
            check("attempt_receipts", 2, len(attempts)),
            check("no_support_response", False, support_response.exists()),
        ]}


SCENARIOS = [scenario_absent_mandatory, scenario_quote_not_backing,
             scenario_altered_source, scenario_partial_derivative,
             scenario_uncertain_remote]


def code_registry():
    return {str(path.relative_to(REPO)): sha_file(path)
            for path in sorted((REPO / "src" / "agora").glob("*.py"))}


def run_battery(out_dir):
    results = []
    for scenario in SCENARIOS:
        with tempfile.TemporaryDirectory(prefix="quality-battery-") as tmp:
            results.append(scenario(Path(tmp)))
    results.sort(key=lambda item: item["id"])
    summary = {"schema": BATTERY, "battery": "quality-battery-v1",
               "scenarios": results,
               "failed": sum(1 for item in results
                             if any(not c["pass"] for c in item["checks"])),
               "provider_calls_live": 0}
    out_dir.mkdir(parents=True, exist_ok=True)
    return summary


def write_results_md(summary):
    lines = ["# Resultados de la batería de calidad v1", "",
             f"Fecha de observación: {summary['date']}. Ejecución offline:",
             "cero llamadas a proveedores vivos; juicios simulados.", "",
             "| Escenario | Comprobación | Esperado | Observado | Resultado |",
             "|---|---|---|---|---|"]
    for scenario in summary["scenarios"]:
        for index, item in enumerate(scenario["checks"]):
            mark = "pass" if item["pass"] else "FAIL"
            name = f"{scenario['id']} {scenario['name']}" if index == 0 else ""
            lines.append(f"| {name} | {item['name']} | {item['expected']} | "
                         f"{item['observed']} | {mark} |")
    lines += ["", f"Escenarios fallidos: {summary['failed']}.",
              "", "Límites: los juicios del proveedor son simulados; esta batería",
              "verifica separación de ejes, procedencia y estados, no calidad",
              "semántica. S1/S3/S4 requieren la fase con modelos y sus puertas.",
              ""]
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true",
                        help="regenerate freeze.json deliberately")
    parser.add_argument("--out", default=str(Path(__file__).parent / "runs" / "run-001"))
    args = parser.parse_args()
    experiment = Path(__file__).parent
    freeze_path = experiment / "freeze.json"
    registry = code_registry()
    runner_sha = sha_file(Path(__file__))
    if args.freeze:
        freeze = {"schema": "agora/quality-battery-freeze/v1",
                  "battery": "quality-battery-v1", "code_registry": registry,
                  "runner_sha256": runner_sha,
                  "scenarios": [s.__name__ for s in SCENARIOS]}
        freeze_path.write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
        print(json.dumps({"status": "frozen", "modules": len(registry)}))
        return 0
    if not freeze_path.exists():
        print(json.dumps({"status": "missing_freeze"}))
        return 2
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze["code_registry"] != registry or freeze["runner_sha256"] != runner_sha:
        print(json.dumps({"status": "code_drift_refusing_run"}))
        return 3
    summary = run_battery(Path(args.out))
    summary["date"] = "2026-10-19"
    results_path = Path(args.out) / "RESULTS.json"
    results_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (experiment / "RESULTS.md").write_text(write_results_md(summary), encoding="utf-8")
    print(json.dumps({"status": "ran", "failed": summary["failed"],
                      "out": args.out}, ensure_ascii=False))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
