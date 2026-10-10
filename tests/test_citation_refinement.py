import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from agora.citation_refinement import SCHEMA, load_refinement


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class CitationRefinementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "refinement.json"
        self.source = b"CPIM\n14. Review project.\n15. Send changes.\n"
        self.claim = "Actividad 14: CPIM reviews the project."
        self.candidate = {"parts": [{"id": "P1", "claims": [{"text": self.claim}]}],
                          "citations": [{"part_id": "P1", "claim_index": 0,
                                         "quote": self.source.decode(),
                                         "matches": [{"start_byte": 0,
                                                      "end_byte": len(self.source)}]}]}
        self.candidate_hash = sha(b"candidate")
        self.selection = {"schema": SCHEMA, "source_sha256": sha(self.source),
                          "candidate_sha256": self.candidate_hash,
                          "claims": [{"part_id": "P1", "claim_index": 0,
                                      "claim_sha256": sha(self.claim.encode()),
                                      "ranges": [{"start_byte": 0, "end_byte": 25,
                                                  "literal_sha256": sha(self.source[:25])}]}]}

    def load(self):
        self.path.write_text(json.dumps(self.selection))
        return load_refinement(self.path, self.source, sha(self.source),
                               self.candidate, self.candidate_hash)

    def test_exact_narrowed_range_is_accepted(self):
        ranges, digest = self.load()
        self.assertEqual(ranges[("P1", 0)], [(0, 25, None)])
        self.assertEqual(digest, sha(self.path.read_bytes()))

    def test_wrong_activity_fails_with_valid_literal_hash(self):
        item = self.selection["claims"][0]["ranges"][0]
        start = self.source.index(b"15.")
        item.update(start_byte=start, end_byte=len(self.source),
                    literal_sha256=sha(self.source[start:]))
        with self.assertRaisesRegex(ValueError, "refinement_activity_mismatch"):
            self.load()

    def test_stale_or_tampered_input_fails(self):
        with self.assertRaisesRegex(ValueError, "invalid_citation_refinement"):
            self.load_with_candidate_hash("0" * 64)
        self.selection["candidate_sha256"] = self.candidate_hash
        self.selection["claims"][0]["ranges"][0]["literal_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "refinement_literal_mismatch"):
            self.load()

    def load_with_candidate_hash(self, value):
        self.selection["candidate_sha256"] = value
        return self.load()

    def test_missing_claim_and_outside_original_citation_fail(self):
        self.selection["claims"] = []
        with self.assertRaisesRegex(ValueError, "invalid_refinement_claim_set"):
            self.load()
        self.selection["claims"] = [{"part_id": "P1", "claim_index": 0,
                                     "claim_sha256": sha(self.claim.encode()),
                                     "ranges": [{"start_byte": 0, "end_byte": 25,
                                                 "literal_sha256": sha(self.source[:25])}]}]
        self.candidate["citations"][0]["matches"][0]["start_byte"] = 25
        with self.assertRaisesRegex(ValueError, "refinement_outside_candidate_citation"):
            self.load()


if __name__ == "__main__":
    unittest.main()
