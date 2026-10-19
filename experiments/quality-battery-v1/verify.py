#!/usr/bin/env python3
"""Integrity and determinism check for the frozen quality battery.

Recomputes the code registry against freeze.json, re-runs the battery in a
temporary directory and compares every check with the committed RESULTS.json.
Fails closed on code drift or any outcome difference.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import code_registry, run_battery, sha_file  # noqa: E402


def main():
    experiment = Path(__file__).parent
    freeze = json.loads((experiment / "freeze.json").read_text(encoding="utf-8"))
    committed = json.loads((experiment / "runs" / "run-001" / "RESULTS.json")
                           .read_text(encoding="utf-8"))
    registry = code_registry()
    if freeze["code_registry"] != registry:
        print(json.dumps({"status": "code_drift", "verdict": "fail"}))
        return 1
    if freeze["runner_sha256"] != sha_file(Path(__file__).parent / "run.py"):
        print(json.dumps({"status": "runner_drift", "verdict": "fail"}))
        return 1
    with tempfile.TemporaryDirectory(prefix="quality-battery-verify-") as tmp:
        fresh = run_battery(Path(tmp))
    if fresh["scenarios"] != committed["scenarios"] or fresh["failed"] != committed["failed"]:
        print(json.dumps({"status": "outcome_mismatch", "verdict": "fail"}))
        return 1
    print(json.dumps({"status": "verified", "failed": committed["failed"],
                      "scenarios": len(committed["scenarios"]),
                      "modules": len(registry)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
