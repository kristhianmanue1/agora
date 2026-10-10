"""Optional Jev advice attached to one completed evidence-answer flow."""

import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

from .evidence_answer_flow import SCHEMA as FLOW_SCHEMA, _save, _sha
from .evidence_answer_flow_v2 import SCHEMA as FLOW_V2_SCHEMA
from .fidelity_cli import request as fidelity_request, CRITERIA

SCHEMA = "agora/jev-flow-review/v1-experimental"
MODEL = "jev-1.13.0"
ENDPOINT = "https://api.typesafe.ai/v1/systemone"


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _preflight(recorded, source):
    recorded = Path(recorded)
    manifest = _read_json(recorded / "result.json")
    if manifest.get("schema") not in (FLOW_SCHEMA, FLOW_V2_SCHEMA) or manifest.get("status") not in (
            "candidate_reviewed", "review_disagreement"):
        raise ValueError("flow_not_reviewable")
    if manifest.get("source_scope") != "supplied_file_only":
        raise ValueError("invalid_source_scope")
    source_raw = Path(source).read_bytes()
    if _sha(source_raw) != manifest["source_sha256"]:
        raise ValueError("source_hash_mismatch")
    stage = manifest.get("stages", {}).get("generation", {})
    if stage.get("status") != "complete" or stage.get("path") != "candidate.json":
        raise ValueError("candidate_not_complete")
    candidate_raw = (recorded / "candidate.json").read_bytes()
    if _sha(candidate_raw) != stage.get("sha256"):
        raise ValueError("candidate_hash_mismatch")
    candidate = json.loads(candidate_raw)
    if candidate.get("source_sha256") != manifest["source_sha256"]:
        raise ValueError("candidate_source_mismatch")
    body = fidelity_request(candidate)
    if body["model"] != MODEL:
        raise ValueError("model_configuration_mismatch")
    return manifest, body, candidate_raw


class LiveJevProvider:
    def __call__(self, body):
        key = os.environ.get("TYPESAFE_API_KEY")
        if not key:
            raise ValueError("provider_key_missing")
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            ENDPOINT, data=raw,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None

        with urllib.request.build_opener(NoRedirect()).open(request, timeout=90) as response:
            reply = response.read(1048577)
        if len(reply) > 1048576 or key.encode() in reply:
            raise ValueError("invalid_provider_response")
        return json.loads(reply)


def review_flow(recorded, source, output, provider):
    """One Jev call at most. Labels remain separate from the GLM review."""
    manifest, body, candidate_raw = _preflight(recorded, source)
    output = Path(output)
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    attempt = {
        "schema": SCHEMA, "status": "attempted", "remote_outcome": "unknown",
        "source_sha256": manifest["source_sha256"],
        "candidate_sha256": _sha(candidate_raw),
        "flow_result_sha256": _sha((Path(recorded) / "result.json").read_bytes()),
        "request_sha256": _sha(json.dumps(body, ensure_ascii=False).encode("utf-8")),
        "model_requested": MODEL, "http_attempts": 1, "retries": 0,
        "adjudication": "not_performed", "memory_admission": "not_performed",
    }
    _save(output / "attempt.json", attempt)
    result = {"schema": SCHEMA, "status": "incomplete", "remote_outcome": "unknown",
              "source_sha256": attempt["source_sha256"],
              "candidate_sha256": attempt["candidate_sha256"],
              "flow_result_sha256": attempt["flow_result_sha256"],
              "model_requested": MODEL, "model_effective": "unknown",
              "adjudication": "not_performed", "memory_admission": "not_performed",
              "disposition": "requires_review", "http_attempts": 1, "retries": 0}
    received = False
    try:
        response = provider(body)
        if not isinstance(response, dict):
            raise ValueError("invalid_provider_response")
        _save(output / "response.json", response)
        received = True
        reported = response.get("model")
        if reported is not None and reported != MODEL:
            raise ValueError("reported_model_mismatch")
        answers = response.get("answers")
        if not isinstance(answers, dict) or set(answers) != set(body["questions"]):
            raise ValueError("invalid_review_answers")
        labels = {}
        for claim_id, answer in answers.items():
            if not isinstance(answer, dict) or answer.get("choice") not in CRITERIA:
                raise ValueError("invalid_review_label")
            labels[claim_id] = answer["choice"]
        result.update(status="advice_available", remote_outcome="received",
                      labels=labels, reported_model=reported,
                      usage_reported=response.get("usage"),
                      jev_aggregate="supported" if all(x == "supported" for x in labels.values()) else "requires_review")
    except Exception as exc:
        result.update(diagnostic=type(exc).__name__,
                      remote_outcome="received" if received else
                      "http_rejected" if isinstance(exc, urllib.error.HTTPError) else "unknown")
        if isinstance(exc, urllib.error.HTTPError):
            result["http_status"] = exc.code
    finally:
        _save(output / "result.json", result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flow-run", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--live-jev", action="store_true", required=True)
    args = parser.parse_args(argv)
    result = review_flow(args.flow_run, args.source, args.out, LiveJevProvider())
    print(json.dumps({"status": result["status"], "output": str(args.out / "result.json"),
                      "http_attempts": result["http_attempts"]}))
    return 0 if result["status"] == "advice_available" else 2


if __name__ == "__main__":
    raise SystemExit(main())
