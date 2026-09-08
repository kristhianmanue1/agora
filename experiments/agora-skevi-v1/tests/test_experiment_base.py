from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import socket
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
SCRIPTS = EXPERIMENT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify_freeze = load("verify_freeze")
prepare_run = load("prepare_run")
runner = load("runner")


class ExperimentBaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lock_path = EXPERIMENT / "experiment.lock.json"
        self.lock = json.loads(self.lock_path.read_text(encoding="utf-8"))

    def test_frozen_documents_and_sections_match(self) -> None:
        result = verify_freeze.verify(ROOT, self.lock_path)
        self.assertEqual([], result["errors"])
        self.assertTrue(result["ok"])

    def test_digest_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            for record in self.lock["documents"].values():
                source = ROOT / record["path"]
                (temp / record["path"]).write_bytes(source.read_bytes())
            baseline = temp / self.lock["documents"]["baseline"]["path"]
            baseline.write_bytes(baseline.read_bytes() + b"\nmutation")
            result = verify_freeze.verify(temp, self.lock_path, check_git=False)
        self.assertFalse(result["ok"])
        self.assertTrue(any(error.startswith("document_digest_mismatch:baseline") for error in result["errors"]))

    def test_intention_to_treat_assignment_and_packs(self) -> None:
        c0 = prepare_run.build_manifest(
            self.lock,
            run_id="pair-1-slot-1",
            pair_id=1,
            slot_id=1,
            base_commit=self.lock["agora_base_commit"],
        )
        c1 = prepare_run.build_manifest(
            self.lock,
            run_id="pair-1-slot-2",
            pair_id=1,
            slot_id=2,
            base_commit=self.lock["agora_base_commit"],
        )
        self.assertEqual("C0", c0["analysis_assignment"])
        self.assertEqual("C1", c1["analysis_assignment"])
        self.assertEqual(["agora-baseline/v1"], [item["id"] for item in c0["instruction_packs"]])
        self.assertEqual(
            ["agora-baseline/v1", "agora-skevi-pilot/v1"],
            [item["id"] for item in c1["instruction_packs"]],
        )

    def test_runtime_contract_change_fails_closed(self) -> None:
        changed = json.loads(json.dumps(self.lock))
        changed["producer"]["model"] = "different-model"
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "experiment.lock.json"
            lock_path.write_text(json.dumps(changed), encoding="utf-8")
            result = verify_freeze.verify(ROOT, lock_path)
        self.assertFalse(result["ok"])
        self.assertIn("runtime_contract_mismatch:producer", result["errors"])

    def test_assignment_tamper_fails_before_launch(self) -> None:
        manifest = prepare_run.build_manifest(
            self.lock,
            run_id="tampered-assignment",
            pair_id=1,
            slot_id=1,
            base_commit=self.lock["agora_base_commit"],
        )
        manifest["condition"] = "C1"
        with self.assertRaisesRegex(ValueError, "intention_to_treat_assignment_mismatch"):
            runner.validate_manifest(manifest, self.lock)

    def test_reported_outcome_failure_is_not_protocol_deviation(self) -> None:
        record = {
            "schema": "agora-skevi/producer-execution-record/v1",
            "provider": "OpenAI",
            "model": "gpt-6-astra",
            "reasoning_effort": "high",
            "model_invocations": 1,
            "input_tokens": 10,
            "output_tokens": 5,
            "status": "failed",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "execution-record.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            observed, errors = runner.validate_execution_record(path, self.lock)
        self.assertEqual([], errors)
        self.assertEqual("failed", observed["status"])

    @unittest.skipUnless(
        os.environ.get("AGORA_ISOLATION_INTEGRATION") == "1",
        "set AGORA_ISOLATION_INTEGRATION=1 outside a parent sandbox",
    )
    def test_runner_isolates_c0_and_seals_evidence(self) -> None:
        manifest = prepare_run.build_manifest(
            self.lock,
            run_id="harness-test-a",
            pair_id=1,
            slot_id=1,
            base_commit=self.lock["agora_base_commit"],
        )
        listener = socket.socket()
        self.addCleanup(listener.close)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        network_port = listener.getsockname()[1]
        adapter_source = f'''#!/usr/bin/python3
import json
import os
import socket
import subprocess
from pathlib import Path

forbidden = Path({str(ROOT / "AGENTS.md")!r})
try:
    forbidden.read_bytes()
    forbidden_readable = True
except OSError:
    forbidden_readable = False

try:
    connection = socket.create_connection(("127.0.0.1", {network_port}), timeout=1)
    connection.close()
    network_connected = True
except OSError:
    network_connected = False

try:
    process_probe = subprocess.run(
        ["/bin/ps", "-p", str(os.getppid()), "-o", "command="],
        capture_output=True,
        text=True,
    )
    process_inspection_blocked = process_probe.returncode != 0
except OSError:
    process_inspection_blocked = True

git_probe = subprocess.run(
    ["/usr/bin/git", "rev-parse", "--is-inside-work-tree"],
    capture_output=True,
    text=True,
)
git_history_visible = git_probe.returncode == 0

workspace = Path(os.environ["AGORA_WORKSPACE"])
instructions = Path(os.environ["AGORA_INPUT_DIR"])
instruction_contains_skevi = any(
    "skevi" in path.read_text(encoding="utf-8").lower() for path in instructions.iterdir()
)
residual = subprocess.Popen(["/bin/sleep", "60"])
(workspace / "artifact.json").write_text(json.dumps({{
    "forbidden_readable": forbidden_readable,
    "network_connected": network_connected,
    "process_inspection_blocked": process_inspection_blocked,
    "git_history_visible": git_history_visible,
    "residual_pid": residual.pid,
    "instruction_files": sorted(path.name for path in instructions.iterdir()),
    "instruction_contains_skevi": instruction_contains_skevi,
    "environment_keys": sorted(os.environ),
}}))
Path(os.environ["AGORA_EXECUTION_RECORD"]).write_text(json.dumps({{
    "schema": "agora-skevi/producer-execution-record/v1",
    "provider": "OpenAI",
    "model": "gpt-6-astra",
    "reasoning_effort": "high",
    "model_invocations": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "status": "completed"
}}))
'''
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            manifest_path = temp / "run.json"
            adapter_path = temp / "adapter.py"
            output = temp / "bundle"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            adapter_path.write_text(adapter_source, encoding="utf-8")
            adapter_path.chmod(0o755)
            result = runner.run(manifest_path, adapter_path, output, timeout_seconds=10)
            if not result["ok"]:
                result["stderr"] = (output / "producer/stderr.log").read_text(errors="replace")
            self.assertTrue(result["ok"], result)
            artifact = json.loads((output / "producer/artifacts/artifact.json").read_text())
            self.assertFalse(artifact["forbidden_readable"])
            self.assertFalse(artifact["network_connected"])
            self.assertTrue(artifact["process_inspection_blocked"])
            self.assertFalse(artifact["git_history_visible"])
            self.assertEqual(["01.md"], artifact["instruction_files"])
            self.assertFalse(artifact["instruction_contains_skevi"])
            self.assertNotIn("GITHUB_TOKEN", artifact["environment_keys"])
            for _ in range(20):
                try:
                    os.kill(artifact["residual_pid"], 0)
                except ProcessLookupError:
                    break
                time.sleep(0.05)
            else:
                self.fail("producer descendant survived runner finalization")
            self.assertTrue((output / "reviewer/input/artifacts/artifact.json").is_file())
            self.assertFalse((output / "reviewer/input/run-manifest.json").exists())
            self.assertEqual("not_run", json.loads((output / "tests/results.json").read_text())["status"])
            self.assertEqual("pending", json.loads((output / "reviewer/review.json").read_text())["status"])
            runner_record = json.loads((output / "producer/runner-record.json").read_text())
            self.assertEqual("valid", runner_record["protocol_status"])
            self.assertEqual("not_evaluated", runner_record["semantic_verdict"])
            integrity = json.loads((output / "integrity/digests.json").read_text())
            for relative, expected in integrity["files"].items():
                observed = hashlib.sha256((output / relative).read_bytes()).hexdigest()
                self.assertEqual(expected, observed)


if __name__ == "__main__":
    unittest.main()
