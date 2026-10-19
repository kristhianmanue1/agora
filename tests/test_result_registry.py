"""Offline checks for the result registry: index, revalidate, fail closed."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from agora.result_registry import RegistryError, get, list_entries, register

ROOT = Path(__file__).resolve().parents[1]


def make_run(root, name, status="candidate_reviewed",
             schema="agora/evidence-answer-flow/v1-experimental", question="What?"):
    run = root / name
    run.mkdir()
    result = {"schema": schema, "status": status, "source_id": "s-1",
              "source_sha256": "a" * 64, "question": question, "dispatches": 5}
    (run / "result.json").write_text(json.dumps(result), encoding="utf-8")
    return run


class ResultRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = self.root / "registry.json"

    def test_register_get_list_roundtrip(self):
        run = make_run(self.root, "run-001")
        entry = register(self.registry, run)
        self.assertEqual(entry["id"], "r-0001")
        self.assertEqual(entry["status"], "candidate_reviewed")
        fetched = get(self.registry, "r-0001")
        self.assertEqual(fetched["manifest"]["question"], "What?")
        self.assertEqual(fetched["entry"]["result_sha256"], entry["result_sha256"])
        self.assertEqual(fetched["replay"], ["--replay-run", str(run.resolve())])
        self.assertEqual(fetched["admission"], "not_performed")
        listing = list_entries(self.registry)
        self.assertEqual((listing["count"], listing["entries"][0]["id"]), (1, "r-0001"))

    def test_ids_advance_and_duplicate_content_is_refused(self):
        first = make_run(self.root, "run-001")
        second = make_run(self.root, "run-002", status="rejected", question="Other?")
        self.assertEqual(register(self.registry, first)["id"], "r-0001")
        self.assertEqual(register(self.registry, second)["id"], "r-0002")
        with self.assertRaisesRegex(RegistryError, "result_already_registered"):
            register(self.registry, first)

    def test_get_fails_closed_on_drift_missing_and_unknown(self):
        run = make_run(self.root, "run-001")
        register(self.registry, run)
        (run / "result.json").write_text(json.dumps({"schema": "tampered"}), encoding="utf-8")
        with self.assertRaisesRegex(RegistryError, "result_drift"):
            get(self.registry, "r-0001")
        (run / "result.json").unlink()
        with self.assertRaisesRegex(RegistryError, "result_file_missing"):
            get(self.registry, "r-0001")
        with self.assertRaisesRegex(RegistryError, "unknown_result_id"):
            get(self.registry, "r-9999")

    def test_unsupported_schema_and_missing_result_are_refused(self):
        with self.assertRaisesRegex(RegistryError, "unsupported_result_schema"):
            register(self.registry, make_run(self.root, "run-bad",
                                             schema="agora/other/v1"))
        with self.assertRaisesRegex(RegistryError, "result_json_not_found"):
            register(self.registry, self.root / "does-not-exist")

    def test_cli_register_get_and_list(self):
        run = make_run(self.root, "run-001")
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
        base = [sys.executable, "-m", "agora.result_registry"]
        register_run = subprocess.run(base + ["register", "--registry", str(self.registry),
                                              "--run", str(run)],
                                      capture_output=True, text=True, env=env)
        self.assertEqual(register_run.returncode, 0)
        self.assertEqual(json.loads(register_run.stdout)["id"], "r-0001")
        get_run = subprocess.run(base + ["get", "--registry", str(self.registry),
                                         "--id", "r-0001"],
                                 capture_output=True, text=True, env=env)
        self.assertEqual(get_run.returncode, 0)
        self.assertEqual(json.loads(get_run.stdout)["manifest"]["dispatches"], 5)
        list_run = subprocess.run(base + ["list", "--registry", str(self.registry)],
                                  capture_output=True, text=True, env=env)
        self.assertEqual(json.loads(list_run.stdout)["count"], 1)
        missing_run = subprocess.run(base + ["get", "--registry", str(self.registry),
                                             "--id", "r-9999"],
                                     capture_output=True, text=True, env=env)
        self.assertEqual(missing_run.returncode, 1)
        self.assertEqual(json.loads(missing_run.stdout)["error"], "unknown_result_id")


if __name__ == "__main__":
    unittest.main()
