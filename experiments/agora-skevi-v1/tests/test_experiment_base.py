from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
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
            self.lock, run_id="pair-1-c0", pair_id=1, condition="C0", base_commit="a" * 40
        )
        c1 = prepare_run.build_manifest(
            self.lock, run_id="pair-1-c1", pair_id=1, condition="C1", base_commit="a" * 40
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


if __name__ == "__main__":
    unittest.main()
