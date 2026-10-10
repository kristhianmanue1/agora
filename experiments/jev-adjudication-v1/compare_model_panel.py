"""Verify locked blind sheets, then unblind and compare without adjudicating."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "model-panel-results"
ROOT = HERE.parents[1]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    sheets = {}
    for reviewer in ("codex", "opencode"):
        path = OUT / (reviewer + "-sheet.json")
        lock = read(OUT / (reviewer + "-lock.json"))
        if sha(path.read_bytes()) != lock["sheet_sha256"] or lock["unblinded"] is not False:
            raise ValueError("sheet_not_locked:" + reviewer)
        sheets[reviewer] = {e["item_id"]: e for e in read(path)["entries"]}
    mapping = read(HERE / "sealed/mapping.json")
    decision = read(HERE / "sealed/decision-lock.json")
    entries = mapping["entries"]
    if {e["item_id"] for e in entries} != set(sheets["codex"]) or set(sheets["codex"]) != set(sheets["opencode"]):
        raise ValueError("item_set_mismatch")
    agreement = {axis: 0 for axis in ("question_clarity", "support", "coverage")}
    rows = []
    for entry in entries:
        iid = entry["item_id"]
        a, b = sheets["codex"][iid], sheets["opencode"][iid]
        for axis in agreement:
            agreement[axis] += a[axis] == b[axis]
        rows.append({
            "item_id": iid,
            "origin": entry["origin"],
            "kind": entry["kind"],
            "codex": {axis: a[axis] for axis in agreement},
            "opencode": {axis: b[axis] for axis in agreement},
            "disagreement_axes": [axis for axis in agreement if a[axis] != b[axis]],
        })
    sentinel = {}
    for iid, expected in decision["sentinels"].items():
        labels = {axis: expected[axis] for axis in ("support", "coverage")}
        sentinel[iid] = {
            "origin": next(e["origin"] for e in entries if e["item_id"] == iid),
            "expected": labels,
            "codex_pass": all(sheets["codex"][iid][axis] == value for axis, value in labels.items()),
            "opencode_pass": all(sheets["opencode"][iid][axis] == value for axis, value in labels.items()),
        }
    jev_paths = {
        "T0-case-03-A": ROOT / "experiments/jev-case-03-review-v1/run-2026-10-10-01/result.json",
        "case-03-omission-control": ROOT / "experiments/jev-case-03-review-v1/control-run-2026-10-10-01/result.json",
        "heldout-datasets-contradiction-control": ROOT / "experiments/jev-heldout-qasper-v1/run-2026-10-10-01/datasets-contradiction-result.json",
    }
    known_jev = {}
    for origin, path in jev_paths.items():
        result = read(path)
        if result["status"] != "completed":
            raise ValueError("prior_jev_not_completed")
        known_jev[origin] = {"labels": result["labels"], "receipt_sha256": sha(path.read_bytes())}
    output = {
        "schema": "agora/model-panel-comparison/v1",
        "status": "compared_not_independently_adjudicated",
        "items": len(rows),
        "agreement": agreement,
        "sentinels": sentinel,
        "known_prior_jev": known_jev,
        "rows": rows,
        "unresolved": [r["item_id"] for r in rows if r["disagreement_axes"]],
        "new_jev_calls": 0,
    }
    path = OUT / "comparison.json"
    if path.exists():
        raise ValueError("comparison_already_exists")
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: output[k] for k in ("status", "items", "agreement", "unresolved", "new_jev_calls")}))


if __name__ == "__main__":
    main()
