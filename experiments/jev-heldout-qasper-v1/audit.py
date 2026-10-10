"""Offline audit of the frozen six-request Jev run; never dispatches."""
import hashlib
import json
from pathlib import Path

import run


def main():
    freeze, freeze_sha, jobs = run.prepare()
    out = run.HERE / "run-2026-10-10-01"
    manifest = json.loads((out / "manifest.json").read_text())
    if manifest != {"freeze_sha256": freeze_sha, "max_calls": len(jobs), "model_requested": freeze["model_requested"], "retries": 0}:
        raise ValueError("manifest_mismatch")
    expected = {c["id"] + "-" + v["id"]: v["expected"] for c in freeze["cases"] for v in c["variants"]}
    if set(expected) != {i for i, _ in jobs} or len(expected) != 6:
        raise ValueError("case_set_mismatch")
    counts = {"support": 0, "coverage": 0, "pair": 0}
    usage = {"input_tokens": 0, "output_tokens": 0}
    rows = []
    for case_id, raw in jobs:
        attempt = json.loads((out / (case_id + "-attempt.json")).read_text())
        result = json.loads((out / (case_id + "-result.json")).read_text())
        request_sha = hashlib.sha256(raw).hexdigest()
        if not (
            attempt["status"] == "attempted"
            and result["status"] == "completed"
            and attempt["request_sha256"] == result["request_sha256"] == request_sha
            and attempt["freeze_sha256"] == result["freeze_sha256"] == freeze_sha
            and result["http_attempts"] == attempt["http_attempts"] == 1
            and result["retries"] == attempt["retries"] == 0
            and result["response"]["model"] == freeze["model_requested"]
        ):
            raise ValueError("receipt_mismatch:" + case_id)
        payload = json.loads(raw)
        state = json.loads(payload["state"])
        if set(payload) != {"model", "state", "questions"} or set(state) != {"task", "requirements", "candidate_answer", "full_source"}:
            raise ValueError("label_leak:" + case_id)
        labels = result["labels"]
        if labels != {axis: result["response"]["answers"][axis]["choice"] for axis in freeze["criteria"]}:
            raise ValueError("label_mismatch:" + case_id)
        for axis in ("support", "coverage"):
            counts[axis] += labels[axis] == expected[case_id][axis]
        counts["pair"] += labels == expected[case_id]
        for k in usage:
            usage[k] += result["response"]["usage"][k]
        rows.append({"id": case_id, "expected": expected[case_id], "observed": labels, "request_sha256": request_sha})
    return {"schema": "agora/jev-heldout-qasper-audit/v1", "status": "verified", "freeze_sha256": freeze_sha, "calls": len(rows), "matches": counts, "usage_reported": usage, "rows": rows}


if __name__ == "__main__":
    result = main()
    path = run.HERE / "run-2026-10-10-01" / "audit.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "calls", "matches", "usage_reported")}))
