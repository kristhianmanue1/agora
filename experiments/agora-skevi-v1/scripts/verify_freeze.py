#!/usr/bin/env python3
"""Verify the frozen Ágora–SKEVI experiment without executing it."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
EXPERIMENT_DIR = HERE.parent
DEFAULT_ROOT = EXPERIMENT_DIR.parents[1]
DEFAULT_LOCK = EXPERIMENT_DIR / "experiment.lock.json"
SECTION_HEADING = re.compile(r"(?m)^### P(\d+)\.[^\n]*\n")
EXPECTED_RUNTIME = {
    "agora_base_commit": "47fb709358a626a8f9c1d35ab442eecfe8a20f41",
    "workspace_projection": {
        "id": "agora-producer-empty-base/v1",
        "include": [],
        "manifest_sha256": "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570",
    },
    "producer": {"provider": "OpenAI", "model": "gpt-6-astra", "reasoning_effort": "high"},
    "reviewer": {"provider": "OpenAI", "model": "gpt-5.6-sol", "reasoning_effort": "high"},
    "pairs": 3,
    "analysis": {
        "primary": "intention-to-treat",
        "secondary": "C0 spontaneous SKEVI-equivalent mechanism rate",
    },
    "budget": {
        "producer_tokens": 150000,
        "producer_model_invocations": 20,
        "producer_active_hours": 4,
        "reviewer_tokens": 30000,
        "reviewer_active_hours": 1,
    },
    "tool_manifest": {
        "id": "agora-producer-tools/v1",
        "network": False,
        "an_kla": False,
        "remote_git_mutation": False,
        "cross_run_access": False,
    },
    "allocation": {
        "method": "sha256 parity of experiment_id, frozen revision and pair id",
        "pairs": {"1": ["C0", "C1"], "2": ["C1", "C0"], "3": ["C0", "C1"]},
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def profile_sections(data: bytes) -> dict[int, bytes]:
    text = data.decode("utf-8")
    headings = list(SECTION_HEADING.finditer(text))
    sections: dict[int, bytes] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections[int(heading.group(1))] = text[heading.start() : end].encode("utf-8")
    return sections


def git_object_exists(root: Path, revision: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def git_file(root: Path, revision: str, path: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def verify(root: Path, lock_path: Path, *, check_git: bool = True) -> dict[str, Any]:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    documents: dict[str, bytes] = {}

    if lock.get("schema") != "agora-skevi/experiment-lock/v1":
        errors.append("unsupported_lock_schema")

    for name, record in lock.get("documents", {}).items():
        path = root / record["path"]
        if not path.is_file():
            errors.append(f"missing_document:{name}:{record['path']}")
            continue
        data = path.read_bytes()
        documents[name] = data
        observed = sha256(data)
        if observed != record["sha256"]:
            errors.append(f"document_digest_mismatch:{name}:{observed}")

    profile = documents.get("profile")
    if profile is not None:
        try:
            sections = profile_sections(profile)
        except UnicodeDecodeError:
            errors.append("profile_not_utf8")
            sections = {}
        for name, record in lock.get("sections", {}).items():
            number = record["profile_section"]
            data = sections.get(number)
            if data is None:
                errors.append(f"missing_profile_section:{name}:P{number}")
                continue
            observed = sha256(data)
            if observed != record["sha256"]:
                errors.append(f"section_digest_mismatch:{name}:{observed}")

    revision = lock.get("frozen_git_revision", "")
    if check_git:
        if not git_object_exists(root, revision):
            errors.append(f"missing_frozen_git_revision:{revision}")
        else:
            for name, record in lock.get("documents", {}).items():
                frozen = git_file(root, revision, record["path"])
                if frozen is None:
                    errors.append(f"missing_frozen_document:{name}:{record['path']}")
                elif sha256(frozen) != record["sha256"]:
                    errors.append(f"frozen_document_digest_mismatch:{name}")
        base_revision = lock.get("agora_base_commit", "")
        if not git_object_exists(root, base_revision):
            errors.append(f"missing_agora_base_commit:{base_revision}")

    expected_conditions = {"C0": ["baseline"], "C1": ["baseline", "profile"]}
    if lock.get("conditions") != expected_conditions:
        errors.append("condition_assignment_mismatch")
    for key, expected in EXPECTED_RUNTIME.items():
        if lock.get(key) != expected:
            errors.append(f"runtime_contract_mismatch:{key}")

    return {
        "schema": "agora-skevi/freeze-verification/v1",
        "experiment_id": lock.get("experiment_id"),
        "frozen_git_revision": revision,
        "ok": not errors,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    args = parser.parse_args()
    result = verify(args.root.resolve(), args.lock.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
