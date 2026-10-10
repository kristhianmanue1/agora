"""One-shot, isolated CTIM sequence probe using Ágora's existing APIs."""

import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from agora import coverage_cli, omission_cli  # noqa: E402
from agora.evidence import query_evidence  # noqa: E402
from agora.plan_generation import live_provider as zai_provider  # noqa: E402
from agora.source import FileSourceAdapter  # noqa: E402

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.txt"
FREEZE = HERE / "freeze.json"
ORIGINAL = Path("/Users/krisnova/www/expertoGobernanza/docs/fuentes/imss/2900-003-001.pdf")
RUNS = HERE / "runs"
QUESTION = json.loads(FREEZE.read_text())["question"]
MODEL = "qwen3:8b"


def local_provider(system, user, *, max_tokens=4096, json_object=True):
    payload = {"model": MODEL, "messages": [{"role": "system", "content": system},
                                            {"role": "user", "content": user}],
               "stream": False, "think": False,
               "options": {"temperature": 0, "num_predict": max_tokens}}
    if json_object:
        payload["format"] = "json"
    request = urllib.request.Request("http://127.0.0.1:11434/api/chat",
                                     data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        raw = response.read(1048577)
    if len(raw) > 1048576:
        raise ValueError("local_provider_response_too_large")
    data = json.loads(raw)
    return {"content": data["message"]["content"],
            "finish_reason": "stop" if data.get("done_reason") == "stop" else data.get("done_reason"),
            "requested_model": MODEL, "reported_model": data.get("model"),
            "usage": {"prompt_tokens": data.get("prompt_eval_count"),
                      "completion_tokens": data.get("eval_count")},
            "response_id": None}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def control_candidate(source_hash, omitted=None):
    lines = SOURCE.read_text().splitlines()
    actions = {number: next(line for line in lines if line.startswith(f"{number}. "))
               for number in range(18, 23)}
    claims = []
    for number, actor in [(18, "CPIM"), (19, "CTIM"), (20, "CTIM"),
                          (21, "CTIM"), (22, "CTIM")]:
        if number != omitted:
            claims.append({"text": f"Actividad {number}, responsable {actor}: {actions[number][4:]}",
                           "quotes": [actions[number]]})
    return {"schema": "agora/claim-evidence-query/v1", "execution_status": "complete",
            "source_sha256": source_hash,
            "parts": [{"id": "P1", "status": "answered", "claims": claims, "missing": []}]}


def review(run_dir, label, candidate, source_hash):
    candidate_path = run_dir / f"{label}-candidate.json"
    save(candidate_path, candidate)
    args = SimpleNamespace(source=str(SOURCE), source_sha256=source_hash,
                           candidate=str(candidate_path), candidate_sha256=sha(candidate_path.read_bytes()),
                           part_id="P1", question=QUESTION, out=str(run_dir / f"{label}-review"),
                           live=True, response=None)
    result = coverage_cli.run(args, lambda path: json.loads(Path(path).read_text()))
    if result["status"] != "complete":
        return {"review": result, "diagnosis": "not_attempted_review_incomplete"}
    review_path = Path(result["output"])
    diagnosis_args = SimpleNamespace(source=str(SOURCE), source_sha256=source_hash,
                                     candidate=str(candidate_path), candidate_sha256=args.candidate_sha256,
                                     part_id="P1", question=QUESTION, review=str(review_path),
                                     review_sha256=sha(review_path.read_bytes()),
                                     out=str(run_dir / f"{label}-diagnosis"), live=True,
                                     response=None, max_output_tokens=4096)
    diagnosis = omission_cli.run(diagnosis_args, lambda path: json.loads(Path(path).read_text()))
    return {"review": result, "diagnosis": diagnosis}


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in ("ollama", "zai"):
        raise SystemExit("usage: run.py RUN_ID ollama|zai")
    run_id = sys.argv[1]
    provider = local_provider if sys.argv[2] == "ollama" else zai_provider
    # The existing review APIs inject a provider only through this module variable.
    coverage_cli.live_provider = provider
    omission_cli.live_provider = provider
    if not run_id.isascii() or not run_id.replace("-", "").isalnum():
        raise SystemExit("invalid_run_id")
    RUNS.mkdir(exist_ok=True)
    run_dir = RUNS / run_id
    run_dir.mkdir(exist_ok=False)
    source_hash = sha(SOURCE.read_bytes())
    manifest = {"schema": "agora/ctim-sequence-run/v1", "status": "started",
                "source_sha256": source_hash, "freeze_sha256": sha(FREEZE.read_bytes()),
                "original_path": str(ORIGINAL), "original_sha256": sha(ORIGINAL.read_bytes()),
                "implementation": {name: sha((ROOT / "src/agora" / name).read_bytes())
                                   for name in ("evidence.py", "coverage_cli.py", "omission_cli.py")},
                "runner_sha256": sha(Path(__file__).read_bytes()),
                "provider": sys.argv[2], "provider_model_requested": MODEL if sys.argv[2] == "ollama" else "glm-5.3-flash",
                "retries": 0,
                "source_status": "manual_visual_transcription_of_page_15",
                "results": {}}
    save(run_dir / "manifest.json", manifest)

    for label, omitted in (("positive", None), ("negative-missing-20", 20)):
        manifest["results"][label] = review(run_dir, label, control_candidate(source_hash, omitted), source_hash)
        save(run_dir / "manifest.json", manifest)

    adapter = FileSourceAdapter(SOURCE, "imss-2900-003-001-p15-manual-excerpt")
    generated = query_evidence(adapter, source_hash, QUESTION,
                               [{"id": "P1", "question": QUESTION}], provider,
                               citation_mode="literal", content_budget=160000)
    save(run_dir / "generated-raw.json", generated)
    manifest["results"]["generated_status"] = generated.get("execution_status")
    save(run_dir / "manifest.json", manifest)
    if generated.get("execution_status") == "complete":
        manifest["results"]["generated"] = review(run_dir, "generated", generated, source_hash)
    else:
        manifest["results"]["generated"] = "not_reviewed_generation_incomplete"
    manifest["status"] = "finished"
    save(run_dir / "manifest.json", manifest)
    print(json.dumps({"run_dir": str(run_dir), "results": manifest["results"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
