import json
from pathlib import Path
import tempfile
import unittest
from agora.source import FileSourceAdapter, digest
from agora.passages import query_passages


class FallbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'source.txt'
        self.data = 'El arranque requiere abonar 73 créditos.\n'.encode()
        self.path.write_bytes(self.data)
        self.sha = digest(self.data)
        self.adapter = FileSourceAdapter(self.path, 'new-fixture')
        self.calls = []

    def provider(self, system, user):
        self.calls.append(json.loads(user))
        return {'finish_reason': 'stop', 'content': json.dumps({'parts': [
            {'id': 'P1', 'status': 'answer', 'answer': '73 créditos.',
             'quotes': ['abonar 73 créditos.']}]})}

    def run_query(self, **options):
        return query_passages(self.adapter, self.sha, '¿Qué desembolso exige iniciar?', self.provider, **options)

    def test_opt_in_restores_exact_source_once(self):
        r = self.run_query(content_budget=5, fallback_source_budget=len(self.data))
        self.assertEqual(r['schema'], 'agora/passage-query/v0.2')
        self.assertEqual(r['execution_status'], 'complete')
        self.assertEqual(r['retrieval']['fallback']['status'], 'used')
        self.assertEqual(r['envelope']['coverage'], 'full')
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0]['document'][0]['text'].encode(), self.data)
        self.assertEqual(r['semantic_support'], 'not_verified')

    def test_default_preserves_no_candidate_outcome(self):
        r = self.run_query()
        self.assertEqual(r['schema'], 'agora/passage-query/v0.1')
        self.assertEqual(r['answer_status'], 'no_retrieval_candidates')
        self.assertEqual(self.calls, [])

    def test_fallback_budget_rejects_whole_source_without_truncation(self):
        r = self.run_query(fallback_source_budget=len(self.data)-1)
        self.assertEqual(r['answer_status'], 'fallback_budget_exhausted')
        self.assertNotIn('envelope', r)
        self.assertEqual(self.calls, [])

    def test_prompt_budget_still_applies(self):
        r = self.run_query(fallback_source_budget=100, prompt_budget=1)
        self.assertEqual(r['diagnostic'], 'prompt_budget_exceeded')
        self.assertEqual(self.calls, [])

    def test_matching_candidate_too_large_is_not_bypass(self):
        r = query_passages(self.adapter, self.sha, 'arranque', self.provider,
                           content_budget=1, fallback_source_budget=100)
        self.assertEqual(r['answer_status'], 'retrieval_budget_exhausted')
        self.assertEqual(r['retrieval']['fallback']['status'], 'not_applicable_matching_candidates')
        self.assertEqual(self.calls, [])

    def test_match_does_not_expand_to_full_source(self):
        r = query_passages(self.adapter, self.sha, 'arranque', self.provider, fallback_source_budget=100)
        self.assertEqual(r['retrieval']['fallback']['status'], 'not_needed')
        self.assertEqual(len(self.calls), 1)

    def test_invalid_budget_and_incompatible_mode(self):
        for value in (0, -1, True, 4194305):
            r = self.run_query(fallback_source_budget=value)
            self.assertEqual(r['diagnostic'], 'invalid_fallback_budget')
        r = self.run_query(mode='source', fallback_source_budget=100)
        self.assertEqual(r['diagnostic'], 'fallback_requires_retrieve')
        self.assertEqual(self.calls, [])

    def test_change_in_source_still_rejected(self):
        self.path.write_bytes(b'changed')
        r = self.run_query(fallback_source_budget=100)
        self.assertEqual(r['diagnostic'], 'source_revision_mismatch')
        self.assertEqual(self.calls, [])


if __name__ == '__main__':
    unittest.main()
