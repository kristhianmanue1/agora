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
EXPECTED_IDENTITY = {
    "schema": "agora-skevi/experiment-lock/v1",
    "experiment_id": "agora-skevi-experiment/v1",
    "frozen_git_revision": "7e7c27cc7911e847bfe1be9dbad6cfe4bd2919bc",
    "documents": {
        "baseline": {
            "id": "agora-baseline/v1",
            "path": "2026-09-07-agora-baseline-v1.md",
            "sha256": "6f6eef7f5ccbc6092cbe563bbbabc80919ec45ddb19c7f6265a400f3a59a516b",
        },
        "profile": {
            "id": "agora-skevi-pilot/v1",
            "path": "2026-09-07-agora-skevi-pilot-v1.md",
            "sha256": "0fc5a51a1479804afa890d5ef59f4940ebf633091aa978bcda74de47b8e4c34e",
        },
        "experiment": {
            "id": "agora-skevi-experiment/v1",
            "path": "2026-09-07-agora-skevi-experiment-v1.md",
            "sha256": "c4610a2d43a829679720d6b5ff49aef206288c75e279295fe5f16b0e5809f668",
        },
    },
    "sections": {
        "fixtures": {
            "profile_section": 3,
            "sha256": "9a0f91e3fc0a4b1598938b7eca21f64b3cf7c65c009ac8d356b2ef6f9a68a28b",
        },
        "repetitions": {
            "profile_section": 4,
            "sha256": "8e87aaea9d18fc1626c80eabb073e185426db930d8c3be22e5f07b1ec044380b",
        },
        "measurement": {
            "profile_section": 5,
            "sha256": "60af577c0fd4884a6bc73af60c387978ac91c1167b247de46de85fde35bee683",
        },
        "isolation": {
            "profile_section": 8,
            "sha256": "e4adbd2024d43d98ca4fbb759759e5faf33667741bf73bfbd147714f0364599d",
        },
        "reviewers": {
            "profile_section": 9,
            "sha256": "46558e17a4c0d0fb76567373fabb9894768e2ca6658f6cfa69fe0768d2337692",
        },
        "decisions": {
            "profile_section": 10,
            "sha256": "4d5aa2a8f6109d99a375e9c53be9a448333ed15813ff963f8a0a54668470798f",
        },
    },
    "conditions": {"C0": ["baseline"], "C1": ["baseline", "profile"]},
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_lock(lock_path: Path) -> dict[str, Any]:
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid_lock:{type(error).__name__}") from error
    if not isinstance(lock, dict):
        raise ValueError("invalid_lock:not_an_object")
    return lock


def profile_sections(data: bytes) -> dict[int, bytes]:
    text = data.decode("utf-8")
    headings = list(SECTION_HEADING.finditer(text))
    sections: dict[int, bytes] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        number = int(heading.group(1))
        if number in sections:
            raise ValueError(f"duplicate_profile_section:P{number}")
        sections[number] = text[heading.start() : end].encode("utf-8")
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


def verify_lock(root: Path, lock: dict[str, Any], *, check_git: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    documents: dict[str, bytes] = {}

    expected_keys = set(EXPECTED_IDENTITY) | set(EXPECTED_RUNTIME)
    if set(lock) != expected_keys:
        errors.append("frozen_lock_shape_mismatch")

    for key, expected in EXPECTED_IDENTITY.items():
        if lock.get(key) != expected:
            errors.append(f"frozen_identity_mismatch:{key}")

    for name, record in EXPECTED_IDENTITY["documents"].items():
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
        except (UnicodeDecodeError, ValueError) as error:
            errors.append(f"profile_section_structure_invalid:{error}")
            sections = {}
        for name, record in EXPECTED_IDENTITY["sections"].items():
            number = record["profile_section"]
            data = sections.get(number)
            if data is None:
                errors.append(f"missing_profile_section:{name}:P{number}")
                continue
            observed = sha256(data)
            if observed != record["sha256"]:
                errors.append(f"section_digest_mismatch:{name}:{observed}")

    revision = EXPECTED_IDENTITY["frozen_git_revision"]
    if check_git:
        if not git_object_exists(root, revision):
            errors.append(f"missing_frozen_git_revision:{revision}")
        else:
            for name, record in EXPECTED_IDENTITY["documents"].items():
                frozen = git_file(root, revision, record["path"])
                if frozen is None:
                    errors.append(f"missing_frozen_document:{name}:{record['path']}")
                elif sha256(frozen) != record["sha256"]:
                    errors.append(f"frozen_document_digest_mismatch:{name}")
        base_revision = lock.get("agora_base_commit", "")
        if not git_object_exists(root, base_revision):
            errors.append(f"missing_agora_base_commit:{base_revision}")

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


def verify(root: Path, lock_path: Path, *, check_git: bool = True) -> dict[str, Any]:
    try:
        lock = load_lock(lock_path)
    except ValueError as error:
        return {
            "schema": "agora-skevi/freeze-verification/v1",
            "experiment_id": None,
            "frozen_git_revision": None,
            "ok": False,
            "errors": [str(error)],
        }
    return verify_lock(root, lock, check_git=check_git)


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
