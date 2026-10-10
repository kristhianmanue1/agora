"""Single negative coverage control using the exact Jev case-03 reviewer contract."""
import hashlib
import importlib.util
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
FREEZE = json.loads((HERE / "control-freeze.json").read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def build_control():
    runner = HERE / "run.py"
    if digest(runner.read_bytes()) != FREEZE["baseline_runner_sha256"]:
        raise ValueError("baseline_runner_changed")
    spec = importlib.util.spec_from_file_location("jev_case03_baseline", runner)
    baseline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(baseline)
    original_raw, original_body, _ = baseline.build_request()
    if digest(original_raw) != FREEZE["baseline_request_sha256"]:
        raise ValueError("baseline_request_changed")
    if FREEZE["source_sha256"] != baseline.SOURCE_SHA256:
        raise ValueError("source_changed")
    candidate_path = baseline.CASE / "A" / "result.json"
    if digest(candidate_path.read_bytes()) != FREEZE["baseline_candidate_file_sha256"]:
        raise ValueError("candidate_changed")
    state = json.loads(original_body["state"])
    claims = state["candidate_answer"]["claims"]
    if len(claims) != 3 or "decreasing order" not in claims[2]["text"]:
        raise ValueError("unexpected_candidate_shape")
    removed = claims.pop(2)
    mutated_body = dict(original_body, state=json.dumps(state, ensure_ascii=False))
    raw = json.dumps(mutated_body, ensure_ascii=False).encode("utf-8")
    if len(raw) > 32768:
        raise ValueError("request_budget_exceeded")
    assert mutated_body["questions"] == original_body["questions"]
    return raw, mutated_body, removed, baseline


def main():
    out = HERE / "control-run-2026-10-10-01"
    if out.exists():
        raise ValueError("run_already_exists")
    raw, body, removed, baseline = build_control()
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        raise ValueError("provider_key_missing")
    out.mkdir(mode=0o700)
    save(out / "control-candidate.json", json.loads(body["state"])["candidate_answer"])
    record = {
        "schema": "agora/jev-case-03-omission-control/v1",
        "status": "attempted",
        "freeze_sha256": digest((HERE / "control-freeze.json").read_bytes()),
        "request_sha256": digest(raw),
        "request_bytes": len(raw),
        "control_candidate_sha256": digest((out / "control-candidate.json").read_bytes()),
        "removed_claim_sha256": digest(json.dumps(removed, ensure_ascii=False).encode("utf-8")),
        "model_requested": baseline.MODEL,
        "endpoint": baseline.ENDPOINT,
        "http_attempts": 1,
        "retries": 0,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "adjudication": "not_performed",
        "memory_admission": "not_performed",
    }
    save(out / "attempt.json", record)
    started = time.monotonic()
    try:
        req = urllib.request.Request(baseline.ENDPOINT, data=raw, headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
        with urllib.request.build_opener(baseline.NoRedirect()).open(req, timeout=90) as response:
            content = response.read(1048577)
        if len(content) > 1048576 or key.encode() in content:
            raise ValueError("invalid_provider_response")
        response = json.loads(content)
        answers = response["answers"]
        if set(answers) != set(baseline.CRITERIA) or any(answers[axis].get("choice") not in baseline.CRITERIA[axis] for axis in baseline.CRITERIA):
            raise ValueError("invalid_provider_answers")
        record.update(status="completed", response=response, labels={axis: answers[axis]["choice"] for axis in baseline.CRITERIA})
    except urllib.error.HTTPError as exc:
        record.update(status="failed", error="HTTPError", http_status=exc.code)
    except Exception as exc:
        record.update(status="failed", error=type(exc).__name__)
    record["elapsed_seconds"] = round(time.monotonic() - started, 3)
    record["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save(out / "result.json", record)
    print(json.dumps({k: record.get(k) for k in ("status", "labels", "error", "http_status", "elapsed_seconds")}))
    return 0 if record["status"] == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
