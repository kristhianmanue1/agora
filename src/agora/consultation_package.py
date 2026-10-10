"""Offline export of a reviewed answer for an explicit external consumer."""

import argparse
import json
from pathlib import Path

from .evidence_answer_flow import SCHEMA as FLOW_SCHEMA, _encoded, _save, _sha
from .evidence_answer_flow_v2 import SCHEMA as FLOW_V2_SCHEMA, validate_budgets
from .jev_flow_review import SCHEMA as JEV_SCHEMA
from .source_evidence_exchange import validate_exchange

SCHEMA = "agora/consultation-package/v1-experimental"


def _linked(run, stage, filename):
    record = stage.get("status")
    if record != "complete" or stage.get("path") != filename:
        raise ValueError("incomplete_stage:" + filename)
    raw = (run / filename).read_bytes()
    if _sha(raw) != stage.get("sha256"):
        raise ValueError("stage_hash_mismatch:" + filename)
    return json.loads(raw)


def build_package(source, flow_run, *, jev_run=None, exchange=None, original=None):
    flow_run = Path(flow_run)
    source_raw = Path(source).read_bytes()
    flow_raw = (flow_run / "result.json").read_bytes()
    flow = json.loads(flow_raw)
    if flow.get("schema") not in (FLOW_SCHEMA, FLOW_V2_SCHEMA) or flow.get("status") not in (
            "candidate_reviewed", "review_disagreement"):
        raise ValueError("flow_not_complete")
    if flow.get("source_scope") != "supplied_file_only":
        raise ValueError("invalid_source_scope")
    if _sha(source_raw) != flow.get("source_sha256"):
        raise ValueError("source_hash_mismatch")
    stages = flow["stages"]
    candidate = _linked(flow_run, stages["generation"], "candidate.json")
    if candidate.get("source_sha256") != flow["source_sha256"]:
        raise ValueError("candidate_source_mismatch")
    claim_stage = stages.get("claim_review", {})
    split = (_linked(flow_run, claim_stage, "split-review.json")
             if claim_stage.get("status") == "complete" else None)
    coverage = _linked(flow_run, stages["coverage"], "coverage.json")
    omission_stage = stages.get("omission", {})
    omission = (_linked(flow_run, omission_stage, "omission.json")
                if omission_stage.get("status") == "complete" else None)
    if coverage.get("source_sha256") != flow["source_sha256"]:
        raise ValueError("coverage_source_mismatch")

    provenance = {"kind": "supplied_utf8", "source_sha256": flow["source_sha256"],
                  "original_integrity": "not_established",
                  "original_document_completeness": "not_established"}
    segments = None
    if exchange is not None:
        if original is None:
            raise ValueError("original_required_for_exchange")
        exchange_raw = Path(exchange).read_bytes()
        exchange_obj = json.loads(exchange_raw)
        segments, derived, integrity = validate_exchange(source, exchange_obj, original)
        if derived != source_raw or integrity != "sha256_verified":
            raise ValueError("exchange_integrity_not_verified")
        provenance = {"kind": "verified_exchange", "source_sha256": flow["source_sha256"],
                      "exchange_sha256": _sha(exchange_raw),
                      "original_sha256": exchange_obj["source"]["sha256"],
                      "original_integrity": integrity,
                      "derivative_coverage": exchange_obj["derivative"]["coverage"],
                      "original_document_completeness": "not_established"}
    elif original is not None:
        raise ValueError("exchange_required_for_original")

    jev = None
    if jev_run is not None:
        jev = json.loads((Path(jev_run) / "result.json").read_text())
        if (jev.get("schema") != JEV_SCHEMA or jev.get("status") != "advice_available" or
                jev.get("flow_result_sha256") != _sha(flow_raw) or
                jev.get("candidate_sha256") != stages["generation"]["sha256"] or
                jev.get("source_sha256") != flow["source_sha256"]):
            raise ValueError("jev_review_mismatch")

    reviews = {(a["part_id"], a["claim_index"]): a for a in split["assessment"]} if split else {}
    claims = []
    expected_jev = set()
    for part in candidate["parts"]:
        for index, claim in enumerate(part["claims"]):
            key = (part["id"], index)
            review = reviews.get(key)
            if split and review is None:
                raise ValueError("missing_claim_review")
            label_id = part["id"] + "_" + str(index)
            expected_jev.add(label_id)
            evidence = []
            citations = [c for c in candidate["citations"]
                         if c["part_id"] == part["id"] and c["claim_index"] == index]
            if not citations:
                raise ValueError("claim_without_citation")
            for citation in citations:
                quote = citation["quote"]
                for match in citation["matches"]:
                    start, end = match["start_byte"], match["end_byte"]
                    if not 0 <= start < end <= len(source_raw) or source_raw[start:end].decode("utf-8") != quote:
                        raise ValueError("citation_mismatch")
                    item = {"start_byte": start, "end_byte": end, "literal_text": quote,
                            "literal_sha256": _sha(source_raw[start:end]),
                            "evidence_id": citation.get("evidence_id")}
                    if segments is not None:
                        matching = [segment for segment in segments.values()
                                    if segment["start_byte"] <= start and end <= segment["end_byte"]]
                        if len(matching) != 1:
                            raise ValueError("citation_unmapped_to_exchange")
                        segment = matching[0]
                        item.update(segment_id=segment["id"], locator=segment["locator"],
                                    modality=segment["modality"],
                                    extraction_status=segment["extraction_status"])
                    evidence.append(item)
            claims.append({"part_id": part["id"], "claim_index": index,
                           "text": claim["text"], "evidence": evidence,
                           "glm_support": review["support"] if review else "not_run",
                           "glm_relevance": review["relevance"] if review else "not_run",
                           "jev_support": jev["labels"].get(label_id) if jev else "not_run"})
    if jev and set(jev["labels"]) != expected_jev:
        raise ValueError("jev_claim_set_mismatch")
    if split and set(reviews) != {(c["part_id"], c["claim_index"]) for c in claims}:
        raise ValueError("claim_review_set_mismatch")
    package = {"schema": SCHEMA, "status": "candidate_for_consumer_review",
            "source": provenance, "source_id": flow["source_id"],
            "question": flow["question"], "requirements": flow["requirements"],
            "claims": claims, "coverage_advice": coverage["coverage"],
            "omission_advice": omission["diagnosis_status"] if omission else "not_run",
            "review_disagreement": bool(omission and omission["review_disagreement"]),
            "glm_model_requested": flow["model_requested"],
            "jev_model_requested": jev["model_requested"] if jev else None,
            "model_effective": "unknown", "flow_result_sha256": _sha(flow_raw),
            "jev_result_sha256": _sha((Path(jev_run) / "result.json").read_bytes()) if jev else None,
            "adjudication": "not_performed", "memory_admission": "not_performed",
            "institutional_acceptance": "not_performed",
            "disposition": "requires_review"}
    if flow["schema"] == FLOW_V2_SCHEMA:
        validate_budgets(flow["budgets"])
        if _sha(_encoded(flow["budgets"])) != flow["budgets_sha256"]:
            raise ValueError("flow_budgets_mismatch")
        package["flow_budgets"] = flow["budgets"]
        package["flow_budgets_sha256"] = flow["budgets_sha256"]
    return package


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--flow-run", required=True, type=Path)
    parser.add_argument("--jev-run", type=Path)
    parser.add_argument("--exchange", type=Path)
    parser.add_argument("--original", type=Path)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--out", type=Path)
    destination.add_argument("--verify-package", type=Path)
    args = parser.parse_args(argv)
    package = build_package(args.source, args.flow_run, jev_run=args.jev_run,
                            exchange=args.exchange, original=args.original)
    if args.verify_package:
        raw = args.verify_package.read_bytes()
        if json.loads(raw) != package:
            raise ValueError("package_mismatch")
        print(json.dumps({"status": "verified", "claims": len(package["claims"]),
                          "package_sha256": _sha(raw)}))
        return 0
    args.out.mkdir(mode=0o700, parents=False, exist_ok=False)
    checksum = _save(args.out / "package.json", package)
    print(json.dumps({"status": package["status"], "claims": len(package["claims"]),
                      "package_sha256": checksum, "output": str(args.out / "package.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
