"""Offline conformance checks for a source-neutral evidence exchange."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
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


def temporal_exchange(root, ident, source_sha256, document_date, media_type, locator, text):
    raw_text = text.encode("utf-8")
    derived = root / (ident + ".txt")
    derived.write_bytes(raw_text)
    manifest = {
        "schema": "agora/source-evidence-exchange/v1",
        "source": {"id": ident, "sha256": source_sha256, "media_type": media_type,
                   "revision": "fixture-declared", "uri": None,
                   "temporal": {"document_date": document_date, "status": "not_assessed"}},
        "derivative": {"id": ident + "-derived", "sha256": hashlib.sha256(raw_text).hexdigest(),
                       "coverage": "partial", "producer": {"system": "fixture", "version": "v1",
                       "manifest_sha256": None, "derivation_id": None},
                       "normalization": {"status": "not_applied", "description": None}},
        "segments": [{"id": "s1", "start_byte": 0, "end_byte": len(raw_text),
                      "sha256": hashlib.sha256(raw_text).hexdigest(), "locator": locator,
                      "modality": "native_text", "extraction_status": "unreviewed"}],
    }
    manifest_raw = json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode()
    return derived, manifest_raw, manifest


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

    def test_five_source_temporal_relation_preserves_literals_without_adjudicating(self):
        fixtures = [
            ("imss-dpm-2000", "719d6da341bff3733750f05357de50ca09fabc7c31c4354186dae8a7a3a70323",
             "2025", "application/pdf", {"kind": "pdf_page", "value":
             {"page": 1, "section": "DPM", "activity": "organización"}},
             "Fixture DPM 2000."),
            ("imss-0500", "ce665959759f74331464471c71dc9cff107e061de09b8be5419a7cf1302e48b7",
             "2022", "application/pdf", {"kind": "pdf_page", "value":
             {"page": 2, "section": "8.1.3", "activity": 2}}, "Fixture IMSS 0500."),
            ("imss-da-1000", "2578bc3df7bafaefd250e971e0087f1b28dc5e9878ed343e8159a23e22d8de49",
             "2025", "application/pdf", {"kind": "pdf_page", "value":
             {"page": 3, "section": "DA", "activity": "1"}}, "Fixture DA 1000."),
            ("imss-procedimiento-2900", "141d9b090efa4d70799ee1368350a5167347b4e8cd5f99912fb192ce6c704faa",
             "2021", "application/pdf", {"kind": "pdf_page", "value":
             {"page": 4, "activity": "2900"}}, "Fixture procedimiento 2900."),
            ("dof-5625913", "e088234e624a6172a7e85eb0aed5c338b55c84e399b6ea086cd326f85ddc580e",
            "2021", "text/html; charset=iso-8859-1", {"kind": "html_fragment", "value":
             {"selector": "#articulo-1", "article": "1"}}, "Fixture DOF 5625913."),
        ]
        with tempfile.TemporaryDirectory() as temp:
            entries = [temporal_exchange(Path(temp), *fixture) for fixture in fixtures]
            exchanges = [(path, raw, manifest, None) for path, raw, manifest in entries]
            hashes = [hashlib.sha256(raw).hexdigest() for _, raw, _ in entries]
            candidate = {"schema": "agora/source-evidence-bundle-candidate/v1",
                         "manifest_sha256s": hashes,
                         "claims": [{"id": "c1", "kind": "relation_candidate",
                         "text": "Candidato: contrastar fechas declaradas 2021 y 2025; no adjudica vigencia.",
                         "relation": {"kind": "temporal_conflict_candidate",
                                      "temporal_status": "not_assessed",
                                      "identity_status": "not_assessed",
                                      "normalization": {"status": "not_applied", "description": None}},
                         "evidence_refs": [{"manifest_sha256": item, "segment_id": "s1",
                                            "start_byte": 0,
                                            "end_byte": entries[index][0].stat().st_size}
                                           for index, item in enumerate(hashes)]}]}
            candidate["claims"].append({"id": "c2", "kind": "relation_candidate",
                "text": "Candidato: la identidad institucional entre DPM y DA no está adjudicada.",
                "relation": {"kind": "identity_unresolved_candidate",
                             "temporal_status": "not_assessed", "identity_status": "not_assessed",
                             "normalization": {"status": "not_applied", "description": None}},
                "evidence_refs": [{"manifest_sha256": hashes[index], "segment_id": "s1",
                                   "start_byte": 0, "end_byte": entries[index][0].stat().st_size}
                                  for index in (0, 2)]})
            result = resolve_bundle(exchanges, candidate)
        claim = result["claims"][0]
        self.assertEqual(claim["relation"]["temporal_status"], "not_assessed")
        self.assertEqual(claim["semantic_support"], "not_verified")
        self.assertFalse(result["admitted"])
        self.assertEqual(result["provider_calls"], 0)
        self.assertEqual([item["source_temporal_status"]["document_date"] for item in claim["evidence"]],
                         ["2025", "2022", "2025", "2021", "2021"])
        self.assertEqual(claim["evidence"][-1]["locator"]["value"]["article"], "1")
        self.assertEqual(claim["evidence"][0]["derivative_normalization"],
                         {"status": "not_applied", "description": None})
        self.assertEqual(result["claims"][1]["relation"]["kind"], "identity_unresolved_candidate")
        self.assertEqual(result["claims"][1]["relation"]["identity_status"], "not_assessed")

    def test_typed_profiles_fail_closed_and_do_not_admit_temporal_vigency(self):
        path, raw, manifest, _ = case("imss-0500")
        wrong = copy.deepcopy(manifest)
        wrong["source"]["temporal"] = {"document_date": "2025", "status": "not_assessed"}
        wrong["source"]["media_type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        with self.assertRaisesRegex(SourceError, "unsupported_source_media_type"):
            validate_exchange(path, wrong)
        wrong = copy.deepcopy(manifest)
        wrong["derivative"]["normalization"] = {"status": "not_applied", "description": None}
        wrong["segments"][0]["locator"]["kind"] = "conversation_turn"
        with self.assertRaisesRegex(SourceError, "unsupported_locator_kind"):
            validate_exchange(path, wrong)
        wrong = copy.deepcopy(manifest)
        wrong["source"]["temporal"] = {"document_date": "2025", "status": "vigente"}
        with self.assertRaisesRegex(SourceError, "invalid_temporal_status"):
            validate_exchange(path, wrong)
        wrong = copy.deepcopy(manifest)
        wrong["derivative"]["normalization"] = {"status": "not_applied", "description": None}
        wrong["segments"][0]["locator"]["value"]["article"] = ["1"]
        with self.assertRaisesRegex(SourceError, "invalid_typed_anchor"):
            validate_exchange(path, wrong)

    def test_iso_8859_1_html_original_keeps_raw_hash_with_utf8_derivative(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = root / "source.html"
            original.write_bytes(b"<p>Coordinaci\xf3n</p>")
            source_sha = hashlib.sha256(original.read_bytes()).hexdigest()
            derived, _, manifest = temporal_exchange(
                root, "html-latin1", source_sha, "2021",
                "text/html; charset=iso-8859-1",
                {"kind": "html_fragment", "value": {"selector": "p"}},
                "Coordinación")
            _, _, integrity = validate_exchange(derived, manifest, original)
            self.assertEqual(integrity, "sha256_verified")
            self.assertNotEqual(source_sha, manifest["derivative"]["sha256"])
            manifest["segments"][0]["locator"]["value"] = {
                "start_byte": 3, "end_byte": 15, "item_id": "html-item-1"}
            validate_exchange(derived, manifest, original)
            manifest["segments"][0]["locator"]["value"]["end_byte"] = 2
            with self.assertRaisesRegex(SourceError, "invalid_html_byte_range"):
                validate_exchange(derived, manifest, original)

    def test_version_relation_stays_candidate_and_requires_declared_kind(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = temporal_exchange(root, "older", "a" * 64, "2021", "text/plain; charset=utf-8",
                                      {"kind": "text_range", "value": {"start_byte": 0, "end_byte": 20}},
                                      "older source literal")
            second = temporal_exchange(root, "later", "b" * 64, "2022", "text/plain; charset=utf-8",
                                       {"kind": "text_range", "value": {"start_byte": 0, "end_byte": 20}},
                                       "later source literal")
            exchanges = [(item[0], item[1], item[2], None) for item in (first, second)]
            hashes = [hashlib.sha256(item[1]).hexdigest() for item in (first, second)]
            candidate = {"schema": "agora/source-evidence-bundle-candidate/v1",
                         "manifest_sha256s": hashes,
                         "claims": [{"id": "amends-candidate", "kind": "relation_candidate",
                         "text": "A source may amend another source.",
                         "evidence_refs": [{"manifest_sha256": item, "segment_id": "s1",
                                            "start_byte": 0, "end_byte": 20} for item in hashes],
                         "relation": {"kind": "version_relation_candidate",
                                      "temporal_status": "not_assessed",
                                      "identity_status": "not_assessed",
                                      "normalization": {"status": "not_applied", "description": None},
                                      "version_relation": "amends"}}]}
            result = resolve_bundle(exchanges, candidate)
            relation = result["claims"][0]["relation"]
            self.assertEqual("amends", relation["version_relation"])
            self.assertEqual("not_assessed", relation["temporal_status"])
            self.assertEqual("not_verified", result["claims"][0]["semantic_support"])
            self.assertFalse(result["admitted"])

    def test_derivative_transformations_travel_with_resolved_evidence(self):
        path, raw, manifest, candidate = case("imss-0500")
        chain = [{"operation": "pdf-text-extraction", "version": "v0.2"},
                 {"operation": "layout-normalization", "version": "2026.10"}]
        manifest["derivative"]["transformations"] = chain
        raw = json.dumps(manifest, ensure_ascii=False).encode()
        candidate["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
        result = resolve(path, raw, manifest, candidate)
        self.assertEqual(result["derivative"]["transformations"], chain)
        evidence = result["claims"][0]["evidence"][0]
        self.assertEqual(evidence["derivative_transformations"], chain)
        self.assertEqual(evidence["derivative_normalization"]["status"], "not_declared")

    def test_derivative_without_transformations_defaults_to_empty_chain(self):
        path, raw, manifest, candidate = case("imss-0500")
        result = resolve(path, raw, manifest, candidate)
        self.assertNotIn("transformations", result["derivative"])
        evidence = result["claims"][0]["evidence"][0]
        self.assertEqual(evidence["derivative_transformations"], [])

    def test_invalid_transformation_chains_are_rejected(self):
        path, raw, manifest, candidate = case("imss-0500")
        for bad in ([{"operation": "extraction"}],
                    [{"operation": "extraction", "version": "v1", "notes": "extra"}],
                    [{"operation": "", "version": "v1"}],
                    [{"operation": "extraction", "version": ""}],
                    "pdf-text-extraction",
                    [{"operation": "extraction", "version": "v1"}] * 9):
            mutated = copy.deepcopy(manifest)
            mutated["derivative"]["transformations"] = bad
            mutated_raw = json.dumps(mutated, ensure_ascii=False).encode()
            fixed = copy.deepcopy(candidate)
            fixed["manifest_sha256"] = hashlib.sha256(mutated_raw).hexdigest()
            with self.assertRaises(SourceError):
                resolve(path, mutated_raw, mutated, fixed)


if __name__ == "__main__":
    unittest.main()
