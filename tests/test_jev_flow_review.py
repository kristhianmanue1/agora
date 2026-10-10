import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from agora.evidence_answer_flow import run_flow
from agora.jev_flow_review import review_flow
from tests.test_evidence_answer_flow import FakeProvider


class JevFlowReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.txt"
        self.source.write_text("Atlas scored 91%.", encoding="utf-8")
        self.source_sha = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.flow = self.root / "flow"
        result = run_flow(self.source, "atlas", self.source_sha,
                          "What was Atlas score?", ["Give the score."],
                          self.flow, FakeProvider())
        self.assertEqual(result["status"], "candidate_reviewed")

    def test_jev_advice_is_linked_and_does_not_change_glm_run(self):
        original = (self.flow / "result.json").read_bytes()
        calls = []

        def provider(body):
            calls.append(body)
            return {"model": "jev-1.13.0", "usage": {"total_tokens": 30},
                    "answers": {key: {"choice": "supported"} for key in body["questions"]}}

        result = review_flow(self.flow, self.source, self.root / "jev", provider)
        self.assertEqual(result["status"], "advice_available")
        self.assertEqual(result["jev_aggregate"], "supported")
        self.assertEqual(result["disposition"], "requires_review")
        self.assertEqual(result["source_sha256"], self.source_sha)
        self.assertEqual(len(calls), 1)
        self.assertEqual((self.flow / "result.json").read_bytes(), original)
        with self.assertRaises(FileExistsError):
            review_flow(self.flow, self.source, self.root / "jev", provider)
        self.assertEqual(len(calls), 1)

    def test_changed_source_rejected_before_attempt(self):
        self.source.write_text("Atlas scored 92%.", encoding="utf-8")
        calls = []
        with self.assertRaisesRegex(ValueError, "source_hash_mismatch"):
            review_flow(self.flow, self.source, self.root / "bad", calls.append)
        self.assertFalse((self.root / "bad").exists())
        self.assertEqual(calls, [])

    def test_timeout_has_one_durable_attempt_and_unknown_remote(self):
        calls = []

        def provider(body):
            calls.append(body)
            self.assertTrue((self.root / "timeout/attempt.json").exists())
            raise TimeoutError("simulated")

        result = review_flow(self.flow, self.source, self.root / "timeout", provider)
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["remote_outcome"], "unknown")
        self.assertEqual(result["http_attempts"], 1)
        self.assertEqual(len(calls), 1)
        self.assertFalse((self.root / "timeout/response.json").exists())


if __name__ == "__main__":
    unittest.main()
