import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from agora.consultation_package import build_package, main
from agora.evidence_answer_flow import run_flow
from agora.jev_flow_review import review_flow
from tests.test_evidence_answer_flow import FakeProvider


class ConsultationPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.txt"
        self.source.write_text("Atlas scored 91%.", encoding="utf-8")
        self.sha = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.flow = self.root / "flow"
        run_flow(self.source, "atlas", self.sha, "What was Atlas score?",
                 ["Give the score."], self.flow, FakeProvider())

    def test_text_package_keeps_axes_and_no_original_claim(self):
        package = build_package(self.source, self.flow)
        self.assertEqual(package["source"]["kind"], "supplied_utf8")
        self.assertEqual(package["source"]["original_integrity"], "not_established")
        self.assertEqual(package["claims"][0]["glm_support"], "supported")
        self.assertEqual(package["claims"][0]["jev_support"], "not_run")
        self.assertEqual(package["memory_admission"], "not_performed")

    def test_rejects_unbounded_source_scope(self):
        manifest_path = self.flow / "result.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["source_scope"] = "unknown"
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "invalid_source_scope"):
            build_package(self.source, self.flow)

    def test_verified_exchange_maps_literal_to_original_locator(self):
        raw = self.source.read_bytes()
        exchange = {"schema": "agora/source-evidence-exchange/v1",
                    "source": {"id": "atlas-original", "sha256": self.sha,
                               "media_type": "text/plain; charset=utf-8",
                               "revision": "fixture-1", "uri": None},
                    "derivative": {"id": "atlas-derived", "sha256": self.sha,
                                   "coverage": "full", "producer": {
                                       "system": "fixture", "version": "1",
                                       "manifest_sha256": None, "derivation_id": None}},
                    "segments": [{"id": "s1", "start_byte": 0, "end_byte": len(raw),
                                  "sha256": self.sha,
                                  "locator": {"kind": "text_range", "value": {
                                      "start_byte": 0, "end_byte": len(raw)}},
                                  "modality": "native_text",
                                  "extraction_status": "unreviewed"}]}
        path = self.root / "exchange.json"
        path.write_text(json.dumps(exchange))
        package = build_package(self.source, self.flow, exchange=path,
                                original=self.source)
        self.assertEqual(package["source"]["original_integrity"], "sha256_verified")
        self.assertEqual(package["claims"][0]["evidence"][0]["segment_id"], "s1")

    def test_jev_link_must_match_exact_flow(self):
        def jev(body):
            return {"model": "jev-1.13.0", "answers": {
                key: {"choice": "supported"} for key in body["questions"]}}
        review_flow(self.flow, self.source, self.root / "jev", jev)
        package = build_package(self.source, self.flow, jev_run=self.root / "jev")
        self.assertEqual(package["claims"][0]["jev_support"], "supported")
        manifest = json.loads((self.flow / "result.json").read_text())
        manifest["question"] = "changed"
        (self.flow / "result.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "jev_review_mismatch"):
            build_package(self.source, self.flow, jev_run=self.root / "jev")

    def test_offline_package_verification_detects_tamper(self):
        output = self.root / "package"
        self.assertEqual(main(["--source", str(self.source), "--flow-run", str(self.flow),
                               "--out", str(output)]), 0)
        package_path = output / "package.json"
        self.assertEqual(main(["--source", str(self.source), "--flow-run", str(self.flow),
                               "--verify-package", str(package_path)]), 0)
        changed = json.loads(package_path.read_text())
        changed["claims"][0]["text"] = "Wrong score"
        package_path.write_text(json.dumps(changed))
        with self.assertRaisesRegex(ValueError, "package_mismatch"):
            main(["--source", str(self.source), "--flow-run", str(self.flow),
                  "--verify-package", str(package_path)])


if __name__ == "__main__":
    unittest.main()
