"""Offline integrity and bounded CTIM 18-22 check for the saved CLI run."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "experiments/ctim-sequence-completeness-v1/source.txt"
FLOW = HERE / "runs/run-2026-10-10-01"
JEV = HERE / "runs/jev-2026-10-10-01"
PACKAGE = HERE / "runs/package-2026-10-10-01/package.json"
SOURCE_SHA = "db72e2fbb43e100102e39beb1d11a5b09eaafb8df76f2c3c8fbc06c6f131ea66"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    source = SOURCE.read_bytes()
    assert sha(source) == SOURCE_SHA
    flow_raw = (FLOW / "result.json").read_bytes()
    flow = json.loads(flow_raw)
    assert flow["status"] == "candidate_reviewed" and flow["dispatches"] == 5
    assert flow["source_sha256"] == SOURCE_SHA
    for stage in flow["stages"].values():
        assert stage["status"] == "complete"
        assert sha((FLOW / stage["path"]).read_bytes()) == stage["sha256"]
    for number in range(1, 6):
        assert len(list(FLOW.glob(f"{number:02d}-*-attempt.json"))) == 1
        assert len(list(FLOW.glob(f"{number:02d}-*-response.json"))) == 1
    candidate = read(FLOW / "candidate.json")
    claims = candidate["parts"][0]["claims"]
    assert len(claims) == 5
    observed = []
    for claim in claims:
        match = re.search(r"actividad (\d+).*?responsable (CPIM|CTIM)", claim["text"])
        assert match is not None
        observed.append((int(match.group(1)), match.group(2)))
    assert observed == [(18, "CPIM"), (19, "CTIM"), (20, "CTIM"), (21, "CTIM"), (22, "CTIM")]
    assert read(FLOW / "coverage.json")["coverage"] == "complete"
    assert read(FLOW / "omission.json")["diagnosis_status"] == "no_omission_found"
    jev = read(JEV / "result.json")
    assert jev["status"] == "advice_available" and jev["http_attempts"] == 1
    assert jev["flow_result_sha256"] == sha(flow_raw)
    assert set(jev["labels"]) == {f"P1_{index}" for index in range(5)}
    package = read(PACKAGE)
    assert package["schema"] == "agora/consultation-package/v1-experimental"
    assert package["flow_result_sha256"] == sha(flow_raw)
    assert package["jev_result_sha256"] == sha((JEV / "result.json").read_bytes())
    assert package["source"]["original_integrity"] == "not_established"
    assert len(package["claims"]) == 5
    for claim in package["claims"]:
        assert claim["evidence"]
        for evidence in claim["evidence"]:
            literal = source[evidence["start_byte"]:evidence["end_byte"]]
            assert literal.decode("utf-8") == evidence["literal_text"]
            assert sha(literal) == evidence["literal_sha256"]
    usage = sum(read(p)["usage"]["total_tokens"] for p in FLOW.glob("*-response.json"))
    print(json.dumps({"status": "verified", "flow_dispatches": 5,
                      "claims": len(claims), "actors": observed,
                      "glm_tokens_reported": usage,
                      "jev_tokens_reported": sum(jev["usage_reported"].values()),
                      "original_integrity": "not_established"}))


if __name__ == "__main__":
    main()
