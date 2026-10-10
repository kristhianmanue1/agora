"""One isolated-context CLI dispatch per named reviewer; no retry."""
import argparse
import hashlib
import json
import shutil
import subprocess
import time
import zipfile
from pathlib import Path

import prepare

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE / "blind.zip"
RUNS = HERE / "runs"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("reviewer", choices=("codex", "opencode"))
    args = parser.parse_args()
    prepare.verify()
    freeze_raw = (HERE / "model-panel-freeze.json").read_bytes()
    freeze = json.loads(freeze_raw)
    prompt_raw = (HERE / "model-review-prompt.txt").read_bytes()
    schema_raw = (HERE / "model-output-schema.json").read_bytes()
    if digest(ARCHIVE.read_bytes()) != freeze["blind_archive_sha256"]:
        raise ValueError("blind_archive_changed")
    reviewer = next(r for r in freeze["reviewers"] if r["id"] == args.reviewer)
    run_dir = RUNS / args.reviewer
    if run_dir.exists():
        raise ValueError("reviewer_already_attempted")
    workdir = run_dir / "workspace"
    workdir.mkdir(parents=True)
    with zipfile.ZipFile(ARCHIVE) as archive:
        names = archive.namelist()
        if len(names) != 8 or any(not n.startswith("blind/") or ".." in Path(n).parts for n in names):
            raise ValueError("unsafe_archive")
        archive.extractall(workdir)
    # The reviewer workspace contains only blind/, with no sibling sealed/.
    if {p.name for p in workdir.iterdir()} != {"blind"}:
        raise ValueError("workspace_not_blind_only")
    if args.reviewer == "codex":
        cmd = [shutil.which("codex"), "exec", "--ephemeral", "--ignore-user-config", "--sandbox", "read-only", "--skip-git-repo-check", "-C", str(workdir), "-m", reviewer["model_requested"], "--output-schema", str(HERE / "model-output-schema.json"), "--output-last-message", str(run_dir / "final.txt"), "--json", "-"]
        stdin = prompt_raw
    else:
        cmd = [shutil.which("opencode"), "run", "--pure", "--model", reviewer["model_requested"], "--agent", "plan", "--dir", str(workdir), "--format", "json", prompt_raw.decode("utf-8")]
        stdin = None
    if not cmd[0]:
        raise ValueError("reviewer_cli_missing")
    attempt = {
        "schema": "agora/model-panel-attempt/v1",
        "reviewer": args.reviewer,
        "status": "attempted",
        "blind_archive_sha256": freeze["blind_archive_sha256"],
        "freeze_sha256": digest(freeze_raw),
        "prompt_sha256": digest(prompt_raw),
        "output_schema_sha256": digest(schema_raw),
        "program": reviewer["program"],
        "model_requested": reviewer["model_requested"],
        "max_dispatches": 1,
        "retries": 0,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "unblinded": False,
    }
    write(run_dir / "attempt.json", attempt)
    started = time.monotonic()
    try:
        result = subprocess.run(cmd, input=stdin, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1800)
        (run_dir / "stdout.log").write_bytes(result.stdout)
        (run_dir / "stderr.log").write_bytes(result.stderr)
        attempt.update(status="returned" if result.returncode == 0 else "failed", exit_code=result.returncode)
    except subprocess.TimeoutExpired as exc:
        (run_dir / "stdout.log").write_bytes(exc.stdout or b"")
        (run_dir / "stderr.log").write_bytes(exc.stderr or b"")
        attempt.update(status="timeout", exit_code=None)
    attempt["elapsed_seconds"] = round(time.monotonic() - started, 3)
    attempt["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    attempt["stdout_sha256"] = digest((run_dir / "stdout.log").read_bytes())
    attempt["stderr_sha256"] = digest((run_dir / "stderr.log").read_bytes())
    final_path = run_dir / "final.txt"
    if final_path.exists():
        attempt["final_sha256"] = digest(final_path.read_bytes())
    write(run_dir / "outcome.json", attempt)
    print(json.dumps({k: attempt.get(k) for k in ("reviewer", "status", "exit_code", "elapsed_seconds", "stdout_sha256", "final_sha256")}))
    return 0 if attempt["status"] == "returned" else 1


if __name__ == "__main__":
    raise SystemExit(main())
