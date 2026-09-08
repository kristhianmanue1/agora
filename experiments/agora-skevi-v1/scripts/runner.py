#!/usr/bin/env python3
"""Execute one producer adapter and seal a mechanical evidence bundle."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import signal
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from isolation import copy_adapter, require_backend, sanitized_environment, seatbelt_profile
from prepare_run import CONDITION_MARKER, DEFAULT_LOCK, DEFAULT_ROOT, blind_identifier, require_commit
from verify_freeze import verify


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_manifest(manifest: dict[str, Any], lock: dict[str, Any]) -> None:
    required = {
        "schema",
        "experiment_id",
        "run_id",
        "pair_id",
        "slot_id",
        "condition",
        "analysis_assignment",
        "agora_base_commit",
        "workspace_projection",
        "instruction_packs",
        "producer",
        "tool_manifest",
        "budget",
        "status",
        "prepared_at",
    }
    if set(manifest) != required:
        raise ValueError("run_manifest_shape_mismatch")
    if manifest["schema"] != "agora-skevi/run-manifest/v1":
        raise ValueError("run_manifest_schema_mismatch")
    if not blind_identifier(manifest["run_id"]):
        raise ValueError("invalid_or_condition_revealing_run_id")
    if manifest["experiment_id"] != lock["experiment_id"]:
        raise ValueError("experiment_id_mismatch")
    pair = manifest["pair_id"]
    slot = manifest["slot_id"]
    if pair not in range(1, lock["pairs"] + 1) or slot not in (1, 2):
        raise ValueError("allocation_coordinates_invalid")
    assigned = lock["allocation"]["pairs"][str(pair)][slot - 1]
    if manifest["condition"] != assigned or manifest["analysis_assignment"] != assigned:
        raise ValueError("intention_to_treat_assignment_mismatch")
    expected_packs = [lock["documents"][key] for key in lock["conditions"][assigned]]
    observed_packs = manifest["instruction_packs"]
    if [item["id"] for item in observed_packs] != [item["id"] for item in expected_packs]:
        raise ValueError("instruction_pack_assignment_mismatch")
    for observed, expected in zip(observed_packs, expected_packs):
        if observed != {key: expected[key] for key in ("id", "path", "sha256")}:
            raise ValueError("instruction_pack_record_mismatch")
    for key in ("producer", "tool_manifest", "budget"):
        if manifest[key] != lock[key]:
            raise ValueError(f"run_manifest_runtime_mismatch:{key}")
    if manifest["agora_base_commit"] != lock["agora_base_commit"]:
        raise ValueError("agora_base_commit_mismatch")
    if manifest["workspace_projection"] != lock["workspace_projection"]:
        raise ValueError("workspace_projection_mismatch")
    require_commit(DEFAULT_ROOT, manifest["agora_base_commit"])


def materialize_workspace(staging: Path, manifest: dict[str, Any]) -> None:
    projection = manifest["workspace_projection"]
    records = []
    workspace = staging / "producer" / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    for relative in projection["include"]:
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("unsafe_workspace_projection_path")
        result = subprocess.run(
            ["git", "show", f"{manifest['agora_base_commit']}:{path.as_posix()}"],
            cwd=DEFAULT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode:
            raise ValueError(f"workspace_projection_missing:{path.as_posix()}")
        destination = workspace / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(result.stdout)
        records.append({"path": path.as_posix(), "sha256": hashlib.sha256(result.stdout).hexdigest()})
    encoded = (json.dumps(records, separators=(",", ":"), sort_keys=True) + "\n").encode()
    observed = hashlib.sha256(encoded).hexdigest()
    if observed != projection["manifest_sha256"]:
        raise ValueError(f"workspace_projection_digest_mismatch:{observed}")
    write_json(staging / "input" / "workspace-projection.json", {"files": records, **projection})


def copy_instruction_packs(staging: Path, manifest: dict[str, Any]) -> None:
    target = staging / "input" / "instructions"
    target.mkdir(parents=True)
    for index, record in enumerate(manifest["instruction_packs"], start=1):
        source = DEFAULT_ROOT / record["path"]
        if digest(source) != record["sha256"]:
            raise ValueError(f"instruction_pack_digest_mismatch:{record['id']}")
        destination = target / f"{index:02d}.md"
        destination.write_bytes(source.read_bytes())


def collect_artifacts(workspace: Path, artifacts: Path) -> None:
    artifacts.mkdir(parents=True)
    for source in sorted(workspace.rglob("*")):
        relative = source.relative_to(workspace)
        if source.is_symlink():
            raise ValueError(f"producer_symlink_forbidden:{relative}")
        if source.is_dir():
            continue
        if relative.as_posix() == ".agora-execution-record.json":
            continue
        destination = artifacts / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


def artifact_patch(artifacts: Path) -> str:
    output: list[str] = []
    for path in sorted(artifacts.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(artifacts).as_posix()
        try:
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        except UnicodeDecodeError:
            output.append(f"Binary artifact {relative} sha256={digest(path)}\n")
            continue
        output.extend(difflib.unified_diff([], lines, fromfile="/dev/null", tofile=f"b/{relative}"))
    return "".join(output)


def validate_execution_record(path: Path, lock: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.is_file():
        return None, ["missing_execution_record"]
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, ["invalid_execution_record"]
    expected_keys = {
        "schema",
        "provider",
        "model",
        "reasoning_effort",
        "model_invocations",
        "input_tokens",
        "output_tokens",
        "status",
    }
    errors = []
    if set(record) != expected_keys or record.get("schema") != "agora-skevi/producer-execution-record/v1":
        errors.append("execution_record_shape_mismatch")
        return record, errors
    for key in ("provider", "model", "reasoning_effort"):
        if record[key] != lock["producer"][key]:
            errors.append(f"producer_identity_mismatch:{key}")
    for key in ("model_invocations", "input_tokens", "output_tokens"):
        if not isinstance(record[key], int) or isinstance(record[key], bool) or record[key] < 0:
            errors.append(f"invalid_nonnegative_integer:{key}")
    if record["status"] not in ("completed", "failed"):
        errors.append("invalid_producer_status")
    if not errors:
        if record["model_invocations"] > lock["budget"]["producer_model_invocations"]:
            errors.append("model_invocation_budget_exceeded")
        if record["input_tokens"] + record["output_tokens"] > lock["budget"]["producer_tokens"]:
            errors.append("token_budget_exceeded")
    return record, errors


def prepare_reviewer_packet(staging: Path) -> None:
    source = staging / "producer" / "artifacts"
    target = staging / "reviewer" / "input" / "artifacts"
    shutil.copytree(source, target)
    shutil.copyfile(staging / "producer" / "patch.diff", staging / "reviewer" / "input" / "patch.diff")


def integrity_manifest(root: Path, run_id: str, experiment_id: str) -> dict[str, Any]:
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.relative_to(root).as_posix() != "integrity/digests.json":
            files[path.relative_to(root).as_posix()] = digest(path)
    return {
        "schema": "agora-skevi/evidence-digests/v1",
        "experiment_id": experiment_id,
        "run_id": run_id,
        "files": files,
        "finalized_at": now(),
    }


def execute_isolated(
    command: list[str],
    *,
    workspace: Path,
    environment: dict[str, str],
    stdout: Any,
    stderr: Any,
    timeout_seconds: float,
) -> tuple[int | None, bool]:
    process = subprocess.Popen(
        command,
        cwd=workspace,
        env=environment,
        stdout=stdout,
        stderr=stderr,
        start_new_session=True,
    )
    timed_out = False
    try:
        exit_code = process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        exit_code = None
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
    return exit_code, timed_out


def run(
    manifest_path: Path,
    adapter_path: Path,
    output: Path,
    *,
    timeout_seconds: float | None = None,
) -> dict[str, Any]:
    freeze = verify(DEFAULT_ROOT, DEFAULT_LOCK)
    if not freeze["ok"]:
        raise RuntimeError(f"freeze_verification_failed:{freeze['errors']}")
    lock = json.loads(DEFAULT_LOCK.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest, lock)

    output = output.resolve()
    if output.exists():
        raise FileExistsError("evidence_output_already_exists")
    if output == DEFAULT_ROOT or DEFAULT_ROOT.resolve() in output.parents:
        raise ValueError("evidence_output_must_be_outside_repository")
    if any(CONDITION_MARKER.search(part) for part in output.parts):
        raise ValueError("evidence_path_reveals_condition")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
    started = now()
    monotonic_start = time.monotonic()
    try:
        write_json(staging / "run-manifest.json", manifest)
        copy_instruction_packs(staging, manifest)
        materialize_workspace(staging, manifest)
        adapter = copy_adapter(adapter_path, staging)
        environment = sanitized_environment(staging)
        profile_path = staging / "integrity" / "producer.sb"
        profile_path.parent.mkdir(parents=True)
        profile_path.write_text(seatbelt_profile(staging), encoding="utf-8")
        workspace = staging / "producer" / "workspace"
        stdout_path = staging / "producer" / "stdout.log"
        stderr_path = staging / "producer" / "stderr.log"
        limit = timeout_seconds or lock["budget"]["producer_active_hours"] * 3600
        backend = require_backend()
        command = [str(backend), "-f", str(profile_path), str(adapter)]
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            exit_code, timed_out = execute_isolated(
                command,
                workspace=workspace,
                environment=environment,
                stdout=stdout,
                stderr=stderr,
                timeout_seconds=limit,
            )

        artifacts = staging / "producer" / "artifacts"
        internal_record = workspace / ".agora-execution-record.json"
        public_record = staging / "producer" / "execution-record.json"
        if internal_record.is_file():
            shutil.copyfile(internal_record, public_record)
        collect_artifacts(workspace, artifacts)
        (staging / "producer" / "patch.diff").write_text(artifact_patch(artifacts), encoding="utf-8")
        producer_record, protocol_deviations = validate_execution_record(public_record, lock)
        outcome_signals = []
        if timed_out:
            protocol_deviations.append("producer_timeout_budget_exceeded")
        if exit_code not in (0, None):
            outcome_signals.append(f"producer_exit_nonzero:{exit_code}")
        if producer_record is not None and producer_record.get("status") == "failed":
            outcome_signals.append("producer_reported_failure")
        execution = {
            "schema": "agora-skevi/runner-execution/v1",
            "started_at": started,
            "finished_at": now(),
            "elapsed_seconds": round(time.monotonic() - monotonic_start, 6),
            "adapter_sha256": digest(adapter),
            "isolation_backend": "macos-sandbox-exec",
            "exit_code": exit_code,
            "timed_out": timed_out,
            "protocol_deviations": protocol_deviations,
            "protocol_status": "valid" if not protocol_deviations else "invalidity_candidate",
            "outcome_signals": outcome_signals,
            "outcome_status": "failure_candidate" if outcome_signals else "no_failure_signaled",
            "semantic_verdict": "not_evaluated",
        }
        write_json(staging / "producer" / "runner-record.json", execution)
        write_json(staging / "tests" / "results.json", {"status": "not_run", "phase": "M1"})
        prepare_reviewer_packet(staging)
        write_json(staging / "reviewer" / "review.json", {"status": "pending", "phase": "M2"})
        for private_path in (
            staging / "producer" / "workspace",
            staging / "producer" / "home",
            staging / "producer" / "tmp",
        ):
            shutil.rmtree(private_path, ignore_errors=True)
        write_json(
            staging / "integrity" / "digests.json",
            integrity_manifest(staging, manifest["run_id"], manifest["experiment_id"]),
        )
        os.replace(staging, output)
        return {
            "ok": not protocol_deviations and not outcome_signals,
            "bundle_finalized": True,
            "protocol_valid": not protocol_deviations,
            "output": str(output),
            "protocol_deviations": protocol_deviations,
            "outcome_signals": outcome_signals,
        }
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-manifest", type=Path, required=True)
    parser.add_argument("--producer-adapter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.run_manifest, args.producer_adapter, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
