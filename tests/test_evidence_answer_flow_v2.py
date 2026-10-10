import hashlib
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from agora.evidence_answer_flow_v2 import (BUDGET_SCHEMA, DEFAULT_BUDGETS,
                                            ZaiProviderV2, run_flow_v2, validate_budgets)
from agora.evidence_answer_flow import ZaiProvider
from tests.test_evidence_answer_flow import FakeProvider


class BudgetTests(unittest.TestCase):
    def test_exact_trailing_break_is_removed_with_raw_receipt_preserved(self):
        raw = '  {"parts": []}\n</br> '
        with patch.object(ZaiProvider, "__call__", return_value={"content": raw}) as call:
            receipt = ZaiProviderV2()("sys", "user", model="glm-5.3-flash",
                                      max_output_tokens=16384, timeout_seconds=180,
                                      json_object=True)
        call.assert_called_once()
        self.assertEqual(receipt["content"], '  {"parts": []}')
        self.assertEqual(receipt["content_original"], raw)
        self.assertEqual(receipt["normalization"]["rule"], "trailing_html_break_v1")
        for bad in ('{"parts": []} junk', '{"parts": []}</br>junk', '{broken}</br>'):
            with self.subTest(content=bad), patch.object(ZaiProvider, "__call__",
                                                   return_value={"content": bad}):
                untouched = ZaiProviderV2()("sys", "user", model="glm-5.3-flash",
                                             max_output_tokens=16384, timeout_seconds=180,
                                             json_object=True)
                self.assertEqual(untouched, {"content": bad})

    def test_default_budget_is_recorded_in_each_actual_attempt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.txt"
            source.write_text("Atlas scored 91%.")
            result = run_flow_v2(source, "atlas", hashlib.sha256(source.read_bytes()).hexdigest(),
                                 "What was Atlas score?", ["Give score."], root / "run",
                                 FakeProvider())
            self.assertEqual(result["status"], "candidate_reviewed")
            self.assertEqual(result["schema"], "agora/evidence-answer-flow/v2-experimental")
            self.assertEqual(result["budgets"], DEFAULT_BUDGETS)
            import json
            attempted = [(root / "run" / name).read_text() for name in
                         ("01-generation-attempt.json", "02-support-attempt.json",
                          "03-relevance-attempt.json", "04-coverage-attempt.json",
                          "05-omission-attempt.json")]
            sizes = [json.loads(raw)["max_output_tokens"] for raw in attempted]
            self.assertEqual(sizes, [16384, 16384, 8192, 4096, 8192])

    def test_budget_limits_fail_before_provider_dispatch(self):
        candidate = dict(DEFAULT_BUDGETS, generation_max_output_tokens=65536,
                         support_max_output_tokens=32768,
                         relevance_max_output_tokens=32768,
                         coverage_max_output_tokens=16384,
                         omission_max_output_tokens=32768)
        with self.assertRaisesRegex(ValueError, "total_output_budget_exceeded"):
            validate_budgets(candidate)
        with self.assertRaisesRegex(ValueError, "invalid_budget_profile"):
            validate_budgets(dict(DEFAULT_BUDGETS, generation_max_output_tokens=True))
        self.assertEqual(DEFAULT_BUDGETS["schema"], BUDGET_SCHEMA)


if __name__ == "__main__":
    unittest.main()
