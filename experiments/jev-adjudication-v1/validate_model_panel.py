"""Freeze two blind model sheets from local CLI outputs, without unblinding."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "exports/model-panel"
OUT = HERE / "model-panel-results"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_output(reviewer):
    run = RUNS / reviewer
    outcome = json.loads((run / "outcome.json").read_text())
    if outcome["status"] != "returned" or outcome["exit_code"] != 0:
        raise ValueError("reviewer_not_returned:" + reviewer)
    raw = (run / "stdout.log").read_bytes()
    if sha(raw) != outcome["stdout_sha256"]:
        raise ValueError("stdout_hash_mismatch:" + reviewer)
    if reviewer == "codex":
        final = (run / "final.txt").read_bytes()
        if sha(final) != outcome["final_sha256"]:
            raise ValueError("final_hash_mismatch")
        sheet = json.loads(final)
        suffix = ""
    else:
        events = [json.loads(line) for line in raw.splitlines()]
        texts = [e["part"]["text"] for e in events if e.get("type") == "text"]
        if not texts:
            raise ValueError("missing_final_text")
        sheet, end = json.JSONDecoder().raw_decode(texts[-1])
        suffix = texts[-1][end:]
    return sheet, suffix, outcome


def validate(sheet):
    if set(sheet) != {"schema", "entries"} or sheet["schema"] != "agora/model-adjudication-sheet/v1":
        raise ValueError("invalid_sheet_shape")
    ids = {p.stem for p in (HERE / "blind/items").glob("*.json")}
    entries = sheet["entries"]
    if len(entries) != 12 or {e["item_id"] for e in entries} != ids:
        raise ValueError("invalid_item_ids")
    fields = {"item_id", "question_clarity", "support", "coverage", "support_evidence", "coverage_evidence", "material_omissions", "notes"}
    for e in entries:
        if set(e) != fields:
            raise ValueError("invalid_entry_fields")
        if e["question_clarity"] not in ("clear", "ambiguous", "uncertain") or e["support"] not in ("supported", "unsupported", "uncertain") or e["coverage"] not in ("complete", "omitted", "justified_abstention", "uncertain"):
            raise ValueError("invalid_label")
        if not all(isinstance(e[k], str) and e[k].strip() for k in ("support_evidence", "coverage_evidence")):
            raise ValueError("missing_evidence")
        if not isinstance(e["material_omissions"], list) or not all(isinstance(v, str) for v in e["material_omissions"]) or not isinstance(e["notes"], str):
            raise ValueError("invalid_notes")
    return {"schema": sheet["schema"], "entries": sorted(entries, key=lambda e: e["item_id"])}


def main():
    if OUT.exists():
        raise ValueError("results_already_locked")
    payloads = {}
    for reviewer in ("codex", "opencode"):
        sheet, suffix, outcome = read_output(reviewer)
        payloads[reviewer] = (validate(sheet), suffix, outcome)
    OUT.mkdir()
    receipts = []
    for reviewer, (sheet, suffix, outcome) in payloads.items():
        path = OUT / (reviewer + "-sheet.json")
        path.write_text(json.dumps(sheet, ensure_ascii=False, indent=2) + "\n")
        receipt = {
            "schema": "agora/model-adjudication-sheet-lock/v1",
            "reviewer": reviewer,
            "model_requested": outcome["model_requested"],
            "model_effective": "unknown: CLI output does not independently verify executor identity",
            "source_stdout_sha256": outcome["stdout_sha256"],
            "sheet_sha256": sha(path.read_bytes()),
            "items": 12,
            "trailing_non_json_text_bytes": len(suffix.encode("utf-8")),
            "unblinded": False,
        }
        receipts.append(receipt)
        (OUT / (reviewer + "-lock.json")).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"locked": [r["reviewer"] for r in receipts], "items_each": 12, "trailing_non_json_text_bytes": {r["reviewer"]: r["trailing_non_json_text_bytes"] for r in receipts}}))


if __name__ == "__main__":
    main()
