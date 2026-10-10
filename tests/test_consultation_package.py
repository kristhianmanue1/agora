import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from agora.consultation_package import MULTI_SEGMENT_SCHEMA, _segment_refs, build_package, main
from agora.evidence_answer_flow import run_flow
from agora.jev_flow_review import review_flow
from tests.test_evidence_answer_flow import FakeProvider


class ConsultationPackageTests(unittest.TestCase):
    def test_omitted_separator_cannot_become_evidence(self):
        raw = b"first\n[omitted]\nsecond\n"
        marker = raw.index(b"[omitted]")
        second = raw.index(b"second")
        segments = {}
        for ident, start, end in (("a", 0, marker), ("b", second, len(raw))):
            segments[ident] = {"id": ident, "start_byte": start, "end_byte": end,
                               "locator": {"kind": "pdf_page", "value": {"page": 15}},
                               "modality": "native_text", "extraction_status": "unreviewed"}
        with self.assertRaisesRegex(ValueError, "citation_unmapped_to_exchange"):
            _segment_refs(0, len(raw), raw, segments)

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

    def test_refined_package_keeps_original_review_scope(self):
        raw = self.source.read_bytes()
        flow = json.loads((self.flow / "result.json").read_text())
        candidate = json.loads((self.flow / "candidate.json").read_text())
        claim = candidate["parts"][0]["claims"][0]
        excerpt = raw[:5]
        refinement = {"schema": "agora/citation-refinement/v1-experimental",
                      "source_sha256": self.sha,
                      "candidate_sha256": flow["stages"]["generation"]["sha256"],
                      "claims": [{"part_id": "P1", "claim_index": 0,
                                  "claim_sha256": hashlib.sha256(claim["text"].encode()).hexdigest(),
                                  "ranges": [{"start_byte": 0, "end_byte": len(excerpt),
                                              "literal_sha256": hashlib.sha256(excerpt).hexdigest()}]}]}
        selection = self.root / "selection.json"
        selection.write_text(json.dumps(refinement))
        with self.assertRaisesRegex(ValueError, "refinement_requires_exchange_and_original"):
            build_package(self.source, self.flow, citation_refinement=selection)
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
        path = self.root / "exchange-refined.json"
        path.write_text(json.dumps(exchange))
        package = build_package(self.source, self.flow, exchange=path,
                                original=self.source, citation_refinement=selection)
        self.assertEqual(package["schema"], "agora/consultation-package/v3-experimental")
        self.assertEqual(package["claims"][0]["evidence"][0]["literal_text"], "Atlas")
        self.assertEqual(package["claims"][0]["glm_support"],
                         "not_reassessed_for_refined_citation")
        self.assertEqual(package["claims"][0]["glm_support_original"], "supported")
        self.assertEqual(package["coverage_advice_scope"], "original_candidate")
        self.assertEqual(package["disposition"], "requires_review")

    def test_contiguous_segments_keep_each_range_and_pdf_locator(self):
        raw = self.source.read_bytes()
        original = self.root / "original.pdf"
        original.write_bytes(b"%PDF-1.4\nfixture bytes")
        split = raw.index(b" scored")
        exchange = {"schema": "agora/source-evidence-exchange/v1",
                    "source": {"id": "atlas-original", "sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
                               "media_type": "application/pdf", "revision": "fixture-1", "uri": None},
                    "derivative": {"id": "atlas-derived", "sha256": self.sha,
                                   "coverage": "partial", "producer": {
                                       "system": "fixture", "version": "1",
                                       "manifest_sha256": None, "derivation_id": None}},
                    "segments": []}
        for index, (start, end) in enumerate(((0, split), (split, len(raw))), 1):
            exchange["segments"].append({"id": f"s{index}", "start_byte": start,
                "end_byte": end, "sha256": hashlib.sha256(raw[start:end]).hexdigest(),
                "locator": {"kind": "pdf_page", "value": {"page": 15,
                    "item_id": f"line-{index}"}}, "modality": "native_text",
                "extraction_status": "unreviewed"})
        path = self.root / "exchange-multi.json"
        path.write_text(json.dumps(exchange))
        package = build_package(self.source, self.flow, exchange=path, original=original)
        self.assertEqual(package["schema"], MULTI_SEGMENT_SCHEMA)
        self.assertEqual(package["source"]["original_integrity"], "sha256_verified")
        evidence = package["claims"][0]["evidence"][0]
        self.assertNotIn("segment_id", evidence)
        self.assertEqual([ref["segment_id"] for ref in evidence["segment_refs"]], ["s1", "s2"])
        self.assertEqual([(ref["start_byte"], ref["end_byte"]) for ref in evidence["segment_refs"]],
                         [(0, split), (split, len(raw))])
        self.assertEqual("".join(ref["literal_text"] for ref in evidence["segment_refs"]),
                         evidence["literal_text"])
        self.assertEqual([ref["locator"]["value"]["item_id"] for ref in evidence["segment_refs"]],
                         ["line-1", "line-2"])

        # Missing a real byte between declared segments must fail closed.
        exchange["segments"][1]["start_byte"] += 1
        exchange["segments"][1]["sha256"] = hashlib.sha256(raw[split + 1:]).hexdigest()
        path.write_text(json.dumps(exchange))
        with self.assertRaisesRegex(ValueError, "citation_unmapped_to_exchange"):
            build_package(self.source, self.flow, exchange=path, original=original)

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

    def test_partial_candidate_conflicts_with_complete_coverage(self):
        class PartialProvider(FakeProvider):
            def __call__(self, system, user, *, model, max_output_tokens,
                         timeout_seconds, json_object):
                request = json.loads(user)
                if "evidence_units" in request and "aspects" in request:
                    item = request["evidence_units"][0]["id"]
                    value = {"parts": [{"id": "P1", "status": "partial",
                             "claims": [{"text": "Atlas scored 91%.",
                                         "evidence_ids": [item]}],
                             "missing": ["The responsible party is unknown."]}]}
                    return {"content": json.dumps(value), "finish_reason": "stop",
                            "requested_model": model, "reported_model": model,
                            "usage": {"total_tokens": 0}}
                return super().__call__(system, user, model=model,
                                        max_output_tokens=max_output_tokens,
                                        timeout_seconds=timeout_seconds,
                                        json_object=json_object)

        partial = self.root / "partial"
        run_flow(self.source, "atlas", self.sha, "What was Atlas score?",
                 ["Give the score."], partial, PartialProvider())
        package = build_package(self.source, partial)
        self.assertEqual(package["schema"], MULTI_SEGMENT_SCHEMA)
        self.assertEqual(package["candidate_answer_status"], "candidate_partial")
        self.assertEqual(package["coverage_advice"], "complete")
        self.assertTrue(package["candidate_coverage_conflict"])
        self.assertEqual(package["candidate_declared_missing"][0]["missing"],
                         ["The responsible party is unknown."])
        self.assertEqual(package["disposition"], "requires_review")

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
