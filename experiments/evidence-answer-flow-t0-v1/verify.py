"""Verify the T0 QASPER freeze against the local source dataset without network calls."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from agora.qasper import eligible, render  # noqa: E402

HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify():
    freeze = json.loads((HERE / "freeze.json").read_text(encoding="utf-8"))
    assert freeze["schema"] == "agora/evidence-answer-flow-t0-freeze/v1"
    dataset_path = ROOT / freeze["dataset"]["path"]
    data = dataset_path.read_bytes()
    assert sha(data) == freeze["dataset"]["sha256"]
    prompt = (HERE / "baseline-prompt.json").read_bytes()
    assert sha(prompt) == freeze["comparison"]["baseline_prompt_sha256"]
    prompt_object = json.loads(prompt)
    assert prompt_object["schema"] == "agora/t0-baseline-prompt/v1"
    papers = json.loads(data)
    assert len(freeze["cases"]) == 6
    assert len({case["document_id"] for case in freeze["cases"]}) == 6
    assert len({case["question_id"] for case in freeze["cases"]}) == 6
    strata = {"answerable": 0, "unanswerable": 0}
    for case in freeze["cases"]:
        paper = papers[case["document_id"]]
        source, paragraphs = render(paper)
        assert len(source) == case["source_bytes"]
        assert sha(source) == case["source_sha256"]
        question = [q for q in paper["qas"] if q["question_id"] == case["question_id"]]
        assert len(question) == 1 and question[0]["question"] == case["question"]
        kind, reason = eligible(question[0], paragraphs)
        assert reason is None and kind == case["stratum"]
        assert len(question[0]["answers"]) == case["annotation_count"]
        encoded_answers = json.dumps(question[0]["answers"], sort_keys=True, ensure_ascii=False).encode()
        assert sha(encoded_answers) == case["reference_answers_sha256"]
        assert case["requirements"] and all(isinstance(x, str) and x.strip() for x in case["requirements"])
        if kind == "answerable":
            for annotation in question[0]["answers"]:
                for evidence in annotation["answer"]["evidence"]:
                    matches = [p for p in paragraphs if p["text"].strip() == evidence.strip()]
                    assert len(matches) == 1
                    match = matches[0]
                    assert source[match["start_byte"]:match["end_byte"]].decode() == match["text"]
        strata[kind] += 1
    assert strata == {"answerable": 4, "unanswerable": 2}
    assert freeze["comparison"]["model_requested"] == "glm-5.3-flash"
    assert freeze["comparison"]["baseline_max_calls"] == 1
    assert freeze["comparison"]["flow_max_calls"] == 5
    return {"status": "verified", "cases": 6, "strata": strata,
            "dataset_sha256": freeze["dataset"]["sha256"]}


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False))
