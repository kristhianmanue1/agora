#!/usr/bin/env python3
"""Prepare a run manifest; never execute an experimental run."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from verify_freeze import DEFAULT_LOCK, DEFAULT_ROOT, verify


ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def require_commit(root: Path, revision: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("base_commit_must_be_full_sha")
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode:
        raise ValueError("base_commit_not_found")
    return revision


def build_manifest(
    lock: dict[str, Any], *, run_id: str, pair_id: int, condition: str, base_commit: str
) -> dict[str, Any]:
    if not ID_PATTERN.fullmatch(run_id):
        raise ValueError("invalid_run_id")
    if pair_id not in range(1, lock["pairs"] + 1):
        raise ValueError("invalid_pair_id")
    if condition not in ("C0", "C1"):
        raise ValueError("invalid_condition")

    packs = []
    for key in lock["conditions"][condition]:
        record = lock["documents"][key]
        packs.append({"id": record["id"], "path": record["path"], "sha256": record["sha256"]})

    return {
        "schema": "agora-skevi/run-manifest/v1",
        "experiment_id": lock["experiment_id"],
        "run_id": run_id,
        "pair_id": pair_id,
        "condition": condition,
        "analysis_assignment": condition,
        "agora_base_commit": base_commit,
        "instruction_packs": packs,
        "producer": lock["producer"],
        "tool_manifest": lock["tool_manifest"],
        "budget": lock["budget"],
        "status": "prepared",
        "prepared_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def write_new(path: Path, payload: dict[str, Any]) -> None:
    path = path.resolve()
    root = DEFAULT_ROOT.resolve()
    if path == root or root in path.parents:
        raise ValueError("output_must_be_outside_repository")
    if path.exists():
        raise FileExistsError("output_already_exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--pair-id", type=int, required=True)
    parser.add_argument("--condition", choices=("C0", "C1"), required=True)
    parser.add_argument("--base-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    verification = verify(DEFAULT_ROOT, DEFAULT_LOCK)
    if not verification["ok"]:
        print(json.dumps(verification, indent=2, sort_keys=True))
        return 1
    lock = json.loads(DEFAULT_LOCK.read_text(encoding="utf-8"))
    base = require_commit(DEFAULT_ROOT, args.base_commit)
    manifest = build_manifest(
        lock,
        run_id=args.run_id,
        pair_id=args.pair_id,
        condition=args.condition,
        base_commit=base,
    )
    write_new(args.output, manifest)
    print(json.dumps({"ok": True, "output": str(args.output.resolve()), "run_id": args.run_id}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
