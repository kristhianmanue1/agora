"""Read-only mechanical audit of the two completed CTIM experiment runs."""

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED_PDF_SHA256 = "141d9b090efa4d70799ee1368350a5167347b4e8cd5f99912fb192ce6c704faa"
ORIGINAL = Path("/Users/krisnova/www/expertoGobernanza/docs/fuentes/imss/2900-003-001.pdf")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def audit(run_name):
    run = HERE / "runs" / run_name
    manifest = read(run / "manifest.json")
    source = (HERE / "source.txt").read_text()
    assert manifest["status"] == "finished"
    assert manifest["source_sha256"] == sha(HERE / "source.txt")
    assert manifest["freeze_sha256"] == sha(HERE / "freeze.json")
    assert manifest["original_sha256"] == sha(ORIGINAL) == EXPECTED_PDF_SHA256
    for label, expected in (("positive", [18, 19, 20, 21, 22]),
                            ("negative-missing-20", [18, 19, 21, 22])):
        candidate = read(run / f"{label}-candidate.json")
        claims = candidate["parts"][0]["claims"]
        assert len(claims) == len(expected)
        for number, claim in zip(expected, claims):
            assert claim["text"].startswith(f"Actividad {number}, responsable ")
            assert claim["quotes"][0] in source
        review = read(run / f"{label}-review" / "result.json")
        diagnosis = read(run / f"{label}-diagnosis" / "result.json")
        assert review["status"] == diagnosis["status"] == "complete"
        for finding in diagnosis["omissions"]:
            for evidence in finding["evidence"]:
                assert source.encode()[evidence["start_byte"]:evidence["end_byte"]].decode() == evidence["text"]
    generated_path = run / "generated-raw.json"
    generated = read(generated_path)
    summary = {"run": run_name, "provider": manifest["provider"],
               "source_and_original_hashes_verified": True,
               "positive": {"review": read(run / "positive-review" / "result.json").get("coverage"),
                            "diagnosis": read(run / "positive-diagnosis" / "result.json").get("diagnosis_status"),
                            "omission_count": len(read(run / "positive-diagnosis" / "result.json")["omissions"])},
               "negative": {"review": read(run / "negative-missing-20-review" / "result.json").get("coverage"),
                            "diagnosis": read(run / "negative-missing-20-diagnosis" / "result.json").get("diagnosis_status"),
                            "omission_count": len(read(run / "negative-missing-20-diagnosis" / "result.json")["omissions"])},
               "generation_status": generated["execution_status"]}
    if generated["execution_status"] == "complete":
        claims = generated["parts"][0]["claims"]
        for claim in claims:
            for quote in claim["quotes"]:
                assert quote in source
        summary["generated_claims"] = len(claims)
        summary["generated_activity_actor_mentions"] = [
            [int(number), actor] for claim in claims
            for number, actor in re.findall(r"actividad\s+(1[89]|2[0-2]).{0,35}?\b(CPIM|CTIM)\b",
                                            claim["text"], re.IGNORECASE)]
        summary["reported_model"] = generated["response"].get("reported_model")
        summary["generated_review"] = read(run / "generated-review" / "result.json").get("coverage")
        summary["generated_diagnosis"] = read(run / "generated-diagnosis" / "result.json").get("diagnosis_status")
    else:
        summary["generation_diagnostics"] = generated.get("diagnostics")
    return summary


if __name__ == "__main__":
    print(json.dumps([audit("run-2026-10-10-c"), audit("run-2026-10-10-d")],
                     ensure_ascii=False, indent=2))
