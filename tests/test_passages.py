import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from agora.passages import query_passages, prepare
from agora.source import FileSourceAdapter, digest


class PassageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'source.txt'
        self.text = 'Proyecto Delta: plazo 12 días.\n\n' + ('Distractor sin relación.\n' * 300) + '\nProyecto Delta: plazo 18 días.\n'
        self.data = self.text.encode()
        self.path.write_bytes(self.data)
        self.sha = digest(self.data)
        self.adapter = FileSourceAdapter(self.path, 'fixture')
        self.calls = []

    def provider(self, quotes, answer='Hay dos plazos: 12 y 18 días.', status='answer'):
        def call(system, user):
            self.calls.append(user)
            return {'finish_reason': 'stop', 'content': json.dumps({'parts': [
                {'id': 'P1', 'status': status, 'answer': answer, 'quotes': quotes}]})}
        return call

    def test_retrieval_finds_distant_evidence_and_localizes_utf8(self):
        quotes = ['plazo 12 días.', 'plazo 18 días.']
        result = query_passages(self.adapter, self.sha, '¿Qué plazo tiene Delta?', self.provider(quotes),
                                content_budget=200)
        self.assertEqual(result['execution_status'], 'complete')
        self.assertEqual(result['envelope']['coverage'], 'partial')
        self.assertEqual(len(self.calls), 1)
        for item in result['citations']:
            for match in item['matches']:
                self.assertEqual(self.data[match['start_byte']:match['end_byte']].decode(), item['quote'])

    def test_empty_search_is_not_source_absence(self):
        result = query_passages(self.adapter, self.sha, '¿Quién pagó matrícula?', self.provider([]))
        self.assertEqual(result['answer_status'], 'no_retrieval_candidates')
        self.assertEqual(result['provider_calls'], 0)
        self.assertEqual(self.calls, [])
        self.assertEqual(result['evidence_sufficiency'], 'unknown')

    def test_oversized_matches_are_not_empty_search(self):
        result = query_passages(self.adapter, self.sha, 'Delta', self.provider([]), content_budget=1)
        self.assertEqual(result['answer_status'], 'retrieval_budget_exhausted')
        self.assertEqual(self.calls, [])

    def test_reference_and_source_have_distinct_coverage(self):
        e, _, _ = prepare(self.adapter, self.sha, 'Plazos', 'source', content_budget=len(self.data))
        self.assertEqual(e['coverage'], 'full')
        e, _, _ = prepare(self.adapter, self.sha, 'Plazos', 'reference', ranges=[(0, 30)])
        self.assertEqual(e['coverage'], 'partial')

    def test_prompt_limit_stops_before_provider(self):
        result = query_passages(self.adapter, self.sha, 'Delta', self.provider([]), prompt_budget=20)
        self.assertEqual(result['diagnostic'], 'prompt_budget_exceeded')
        self.assertEqual(self.calls, [])

    def test_revision_change_stops_before_provider(self):
        self.path.write_bytes(b'changed')
        result = query_passages(self.adapter, self.sha, 'Delta', self.provider([]))
        self.assertEqual(result['diagnostic'], 'source_revision_mismatch')
        self.assertEqual(self.calls, [])

    def test_quote_across_passage_boundary_rejected(self):
        self.path.write_bytes(b'alpha---beta')
        result = query_passages(self.adapter, digest(b'alpha---beta'), 'Test',
                               self.provider(['alpha\nbeta']), 'reference', ranges=[(0, 5), (8, 12)])
        self.assertEqual(result['execution_status'], 'rejected')
        self.assertEqual(result['diagnostic'], 'quote_outside_literal_passage')

    def test_locator_text_cannot_be_cited(self):
        result = query_passages(self.adapter, self.sha, 'Delta', self.provider(['passage']))
        self.assertEqual(result['execution_status'], 'rejected')

    def test_model_abstention_keeps_limited_scope(self):
        result = query_passages(self.adapter, self.sha, 'Delta', self.provider([], '', 'not_in_document'))
        self.assertEqual(result['answer_status'], 'not_found_in_supplied_material')
        self.assertNotIn('not_in_source', json.dumps(result))

    def test_provider_failure_retains_selection(self):
        def fail(*args):
            raise TimeoutError('sensitive detail')
        result = query_passages(self.adapter, self.sha, 'Delta', fail)
        self.assertEqual(result['execution_status'], 'failed')
        self.assertEqual(result['diagnostic'], 'TimeoutError')
        self.assertIn('envelope', result)
        self.assertNotIn('sensitive detail', json.dumps(result))

    def test_http_error_keeps_status_without_body_or_reason(self):
        def fail(*args):
            raise HTTPError('https://example.invalid', 401, 'sensitive reason', {}, None)
        result = query_passages(self.adapter, self.sha, 'Delta', fail)
        self.assertEqual(result['transport_error'], {'kind': 'http_error', 'status': 401})
        self.assertNotIn('sensitive reason', json.dumps(result))
        self.assertNotIn('example.invalid', json.dumps(result))

    def test_invalid_mode_does_not_call_provider(self):
        result = query_passages(self.adapter, self.sha, 'Delta', self.provider([]), mode='unknown')
        self.assertEqual(result['execution_status'], 'rejected')
        self.assertEqual(self.calls, [])


if __name__ == '__main__':
    unittest.main()
