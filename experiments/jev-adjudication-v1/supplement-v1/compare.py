"""Compare two already locked blind sheets with the frozen heldout controls."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
ROOT = HERE.parents[2]


def read(path):
    return json.loads(path.read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    sheets = {}
    for reviewer in ("codex", "opencode"):
        path = OUT / (reviewer + "-sheet.json")
        lock = read(OUT / (reviewer + "-lock.json"))
        if sha(path.read_bytes()) != lock["sheet_sha256"] or lock["unblinded"] is not False:
            raise ValueError("sheet_not_locked:" + reviewer)
        sheets[reviewer] = {e["item_id"]: e for e in read(path)["entries"]}
    mapping = read(HERE / "sealed/mapping.json")["entries"]
    if {e["item_id"] for e in mapping} != set(sheets["codex"]) or set(sheets["codex"]) != set(sheets["opencode"]):
        raise ValueError("item_set_mismatch")
    previous = {}
    for case in ("datasets", "baselines"):
        for variant in ("complete", "omission"):
            path = ROOT / f"experiments/jev-heldout-qasper-v1/run-2026-10-10-01/{case}-{variant}-result.json"
            raw = path.read_bytes()
            result = json.loads(raw)
            if result["status"] != "completed":
                raise ValueError("prior_jev_not_completed:" + case + ":" + variant)
            previous[(case, variant)] = {"labels": result["labels"], "receipt_sha256": sha(raw)}
    rows = []
    for entry in mapping:
        iid = entry["item_id"]
        a, b = sheets["codex"][iid], sheets["opencode"][iid]
        rows.append({
            "item_id": iid,
            "case": entry["case"],
            "variant": entry["variant"],
            "expected": entry["expected"],
            "codex": {axis: a[axis] for axis in ("question_clarity", "support", "coverage")},
            "opencode": {axis: b[axis] for axis in ("question_clarity", "support", "coverage")},
            "prior_jev": previous[(entry["case"], entry["variant"])],
        })
    output = {"schema": "agora/jev-disputed-omission-comparison/v1", "status": "compared_not_human_adjudicated", "rows": rows, "new_jev_calls": 0}
    path = OUT / "comparison.json"
    if path.exists():
        if read(path) != output:
            raise ValueError("comparison_changed")
        print(json.dumps({"verified": True, "rows": len(rows), "status": output["status"]}))
    else:
        path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"created": True, "rows": len(rows), "status": output["status"]}))


if __name__ == "__main__":
    main()
