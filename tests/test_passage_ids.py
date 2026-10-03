import json
import tempfile
import unittest
from pathlib import Path
from agora.passages import query_passages
from agora.source import FileSourceAdapter, digest

class PassageIdTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'source.txt'
        self.raw = 'La evaluación usa 1–5; el valor positivo es INLINEFORM0.\n\nSe excluye la nota 2.'.encode()
        self.path.write_bytes(self.raw)
        self.adapter = FileSourceAdapter(self.path, 'unicode-test')
        self.calls = 0

    def run_case(self, mutate=None, **options):
        def provider(system, user):
            self.calls += 1
            payload = json.loads(user)
            self.assertIn('2000 characters', system)
            units = payload['evidence_units']
            response = {'finish_reason': 'stop', 'content': json.dumps({'parts': [{
                'id': 'P1', 'status': 'partial',
                'claims': [{'text': 'Se excluye la nota 2.', 'evidence_ids': [units[-1]['id']]}],
                'missing': ['El umbral positivo no es legible.']}]})}
            if mutate: mutate(response, units)
            return response
        return query_passages(self.adapter, digest(self.raw), '¿Cómo se etiqueta?', provider,
                              citation_mode='ids', mode=options.pop('mode', 'source'), **options)

    def test_source_ids_resolve_exact_utf8_and_keep_missing(self):
        r = self.run_case()
        self.assertEqual(r['schema'], 'agora/passage-query/v0.4')
        self.assertEqual(r['answer_status'], 'candidate_partial')
        self.assertEqual(r['semantic_support'], 'not_verified')
        self.assertFalse(r['document_absence_established'])
        self.assertEqual(self.calls, 1)
        for c in r['citations']:
            m=c['matches'][0]
            self.assertEqual(self.raw[m['start_byte']:m['end_byte']].decode(), c['quote'])

    def test_unknown_id_rejected_without_retry(self):
        def mutate(r, units): r['content']=r['content'].replace(units[-1]['id'], 'ev_invented')
        r=self.run_case(mutate)
        self.assertEqual(r['diagnostic'], 'unknown_evidence_id')
        self.assertEqual(self.calls, 1)
        self.assertNotIn('answer', r)

    def test_duplicate_id_rejected(self):
        def mutate(r, units):
            d=json.loads(r['content']);d['parts'][0]['claims'][0]['evidence_ids']*=2;r['content']=json.dumps(d)
        self.assertEqual(self.run_case(mutate)['diagnostic'], 'duplicate_evidence_id')

    def test_truncation_never_salvaged(self):
        def mutate(r, units): r['finish_reason']='length'
        self.assertEqual(self.run_case(mutate)['diagnostic'], 'generation_incomplete')

    def test_total_text_limit_is_enforced(self):
        def mutate(r, units):
            d=json.loads(r['content']);d['parts'][0]['claims'][0]['text']='x'*2000;r['content']=json.dumps(d)
        self.assertEqual(self.run_case(mutate)['diagnostic'], 'response_text_budget_exceeded')

    def test_partial_source_preserves_expansion_requirement(self):
        r=self.run_case(mode='reference', ranges=[(0, self.raw.index(b'\n\n'))])
        self.assertEqual(r['answer_status'], 'candidate_requires_expansion')
        self.assertTrue(r['requires_expansion'])

    def test_prompt_budget_stops_before_call(self):
        r=self.run_case(prompt_budget=200)
        self.assertEqual(r['diagnostic'], 'prompt_budget_exceeded')
        self.assertEqual(self.calls, 0)

    def test_changed_source_rejected_before_call(self):
        self.path.write_bytes(b'changed')
        self.assertEqual(self.run_case()['diagnostic'], 'source_revision_mismatch')
        self.assertEqual(self.calls, 0)

if __name__ == '__main__': unittest.main()
