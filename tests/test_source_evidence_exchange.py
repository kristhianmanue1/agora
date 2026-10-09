"""Offline conformance checks for a source-neutral evidence exchange."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from agora.source import SourceError
from agora.source_evidence_exchange import resolve, resolve_bundle, validate_exchange

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "source-evidence-exchange-v1"


def case(name):
    raw = (EXAMPLES / f"{name}-manifest.json").read_bytes()
    manifest = json.loads(raw)
    candidate = json.loads((EXAMPLES / f"{name}-candidate.json").read_bytes())
    return EXAMPLES / f"{name}-derived.txt", raw, manifest, candidate


class EvidenceExchangeTests(unittest.TestCase):
    def test_imss_0500_literal_and_interpretation_stay_separate(self):
        path, raw, manifest, candidate = case("imss-0500")
        result = resolve(path, raw, manifest, candidate)
        self.assertEqual(result["original_integrity"], "not_checked")
        self.assertEqual(result["source"]["sha256"],
                         "ce665959759f74331464471c71dc9cff107e061de09b8be5419a7cf1302e48b7")
        self.assertEqual(result["claims"][0]["kind"], "interpretation_candidate")
        evidence = result["claims"][0]["evidence"][0]
        self.assertEqual(evidence["literal_text"], "8.1.3 Dirección de Prestaciones Médicas\n")
        self.assertEqual(evidence["locator"], {"kind": "pdf_page", "value": {"page": 45, "section": "8.1.3"}})
        self.assertEqual(evidence["extraction_status"], "unreviewed")
        self.assertEqual(result["claims"][0]["semantic_support"], "not_verified")
        self.assertFalse(result["admitted"])
        self.assertEqual(result["provider_calls"], 0)

    def test_other_project_source_verifies_original_and_optional_producer(self):
        path, raw, manifest, candidate = case("skevi")
        manifest["derivative"]["producer"] = {
            "system": "skopos", "version": "fixture-v1", "manifest_sha256": "a" * 64,
            "derivation_id": "synthetic-only"}
        raw = json.dumps(manifest, ensure_ascii=False).encode()
        candidate["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
        result = resolve(path, raw, manifest, candidate, EXAMPLES / "skevi-source.txt")
        self.assertEqual(result["original_integrity"], "sha256_verified")
        self.assertEqual(result["derivative"]["producer"]["system"], "skopos")
        self.assertEqual(result["claims"][0]["kind"], "relation_candidate")
        self.assertEqual(result["claims"][0]["evidence"][0]["literal_text"],
                         (EXAMPLES / "skevi-source.txt").read_text())

    def test_two_imss_manuals_remain_separate_sources_with_candidate_relation(self):
        entries = [case("imss-0500"), case("imss-2000")]
        exchanges = [(path, raw, manifest, None) for path, raw, manifest, _ in entries]
        candidate = json.loads((EXAMPLES / "imss-cross-manual-candidate.json").read_bytes())
        result = resolve_bundle(exchanges, candidate)
        evidence = result["claims"][0]["evidence"]
        self.assertEqual([item["locator"]["value"]["page"] for item in evidence], [45, 172])
        self.assertEqual([item["source_sha256"] for item in evidence],
                         [entry[2]["source"]["sha256"] for entry in entries])
        self.assertEqual([item["modality"] for item in evidence], ["native_text", "native_text"])
        self.assertEqual(result["claims"][0]["semantic_support"], "not_verified")
        self.assertFalse(result["admitted"])
        self.assertEqual(result["provider_calls"], 0)
        wrong = copy.deepcopy(candidate)
        wrong["claims"][0]["evidence_refs"][1]["manifest_sha256"] = wrong["manifest_sha256s"][0]
        with self.assertRaisesRegex(SourceError, "evidence_outside_segment|relation_requires_multiple_sources"):
            resolve_bundle(exchanges, wrong)

    def test_two_derivatives_of_one_original_are_not_two_sources(self):
        first = case("imss-0500")
        second = case("imss-2000")
        same_original = copy.deepcopy(second[2])
        same_original["source"]["sha256"] = first[2]["source"]["sha256"]
        second_raw = json.dumps(same_original, ensure_ascii=False).encode()
        exchanges = [(first[0], first[1], first[2], None),
                     (second[0], second_raw, same_original, None)]
        candidate = json.loads((EXAMPLES / "imss-cross-manual-candidate.json").read_bytes())
        second_sha = hashlib.sha256(second_raw).hexdigest()
        candidate["manifest_sha256s"][1] = second_sha
        candidate["claims"][0]["evidence_refs"][1]["manifest_sha256"] = second_sha
        with self.assertRaisesRegex(SourceError, "relation_requires_multiple_sources"):
            resolve_bundle(exchanges, candidate)

    def test_changed_identity_locator_and_utf8_are_rejected(self):
        path, raw, manifest, candidate = case("imss-0500")
        wrong = copy.deepcopy(candidate)
        wrong["manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(SourceError, "manifest_sha256_mismatch"):
            resolve(path, raw, manifest, wrong)
        wrong = copy.deepcopy(manifest)
        wrong["segments"][0]["locator"]["value"]["page"] = 0
        with self.assertRaisesRegex(SourceError, "invalid_pdf_page"):
            validate_exchange(path, wrong)
        wrong = copy.deepcopy(candidate)
        wrong["claims"][0]["evidence_refs"][0]["start_byte"] = path.read_bytes().index("ó".encode()) + 1
        with self.assertRaisesRegex(SourceError, "evidence_splits_utf8"):
            resolve(path, raw, manifest, wrong)
        wrong = copy.deepcopy(candidate)
        wrong["claims"][0]["evidence_refs"][0]["segment_id"] = "absent"
        with self.assertRaisesRegex(SourceError, "unknown_segment_id"):
            resolve(path, raw, manifest, wrong)

    def test_changed_source_and_segment_are_rejected(self):
        path, raw, manifest, candidate = case("skevi")
        with self.assertRaisesRegex(SourceError, "original_sha256_mismatch"):
            resolve(path, raw, manifest, candidate, EXAMPLES / "imss-0500-derived.txt")
        wrong = copy.deepcopy(manifest)
        wrong["segments"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(SourceError, "segment_sha256_mismatch"):
            validate_exchange(path, wrong)
        wrong = copy.deepcopy(candidate)
        wrong["claims"][0]["evidence_refs"][0]["end_byte"] += 1
        with self.assertRaisesRegex(SourceError, "evidence_outside_segment"):
            resolve(path, raw, manifest, wrong)

    def test_cli_example_resolves_without_provider(self):
        cmd = [sys.executable, "-m", "agora.source_evidence_exchange", "resolve",
               "--derived", str(EXAMPLES / "skevi-derived.txt"),
               "--manifest", str(EXAMPLES / "skevi-manifest.json"),
               "--candidate", str(EXAMPLES / "skevi-candidate.json"),
               "--original", str(EXAMPLES / "skevi-source.txt")]
        run = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["status"], "candidate_unreviewed")
        self.assertEqual(result["provider_calls"], 0)


if __name__ == "__main__":
    unittest.main()
