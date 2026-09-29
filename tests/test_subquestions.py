import tempfile
import unittest
from pathlib import Path
from agora.source import FileSourceAdapter, SourceError, digest
from agora.subquestions import prepare_subquestions


class SubquestionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'source.txt'
        self.raw = ('Alfa: aprobación.\n\n' + 'Distractor.\n\n' * 20 + 'Beta: adquisición.').encode()
        self.path.write_bytes(self.raw)
        self.adapter = FileSourceAdapter(self.path, 'test')
        self.sha = digest(self.raw)
        self.spec = {'schema': 'agora/subquestions-input/v1-experimental', 'questions': [
            {'id': 'a', 'query': 'Alfa', 'reference_ranges': [[0, len('Alfa: aprobación.'.encode())]]},
            {'id': 'b', 'query': 'Beta', 'reference_ranges': [[self.raw.index(b'Beta'), len(self.raw)]]}]}

    def test_distant_evidence_budget_and_no_semantic_promotion(self):
        r = prepare_subquestions(self.adapter, self.sha, self.spec, 100)
        self.assertEqual([q['reference_coverage'] for q in r['questions']], ['covered', 'covered'])
        self.assertLessEqual(r['delivered_bytes'], 100)
        self.assertEqual(r['global_completeness'], 'not_established')
        self.assertEqual(r['provider_calls'], 0)

    def test_tiny_quota_reports_missing_not_absence(self):
        r = prepare_subquestions(self.adapter, self.sha, self.spec, 2)
        self.assertIsNone(r['envelope'])
        self.assertTrue(all(q['missing_reference_ranges'] for q in r['questions']))
        self.assertEqual(r['semantic_support'], 'not_verified')

    def test_missing_reference_is_unknown_even_with_hits(self):
        self.spec['questions'][0]['reference_ranges'] = []
        self.assertEqual(prepare_subquestions(self.adapter, self.sha, self.spec, 100)['questions'][0]['reference_coverage'], 'unknown')

    def test_overlapping_candidates_are_deduplicated(self):
        self.spec['questions'][1]['query'] = 'Alfa'
        r = prepare_subquestions(self.adapter, self.sha, self.spec, 100)
        self.assertEqual(r['questions'][1]['reference_coverage'], 'partial')
        spans = r['envelope']['spans']
        self.assertEqual(r['delivered_bytes'], sum(s['end_byte']-s['start_byte'] for s in spans))

    def test_stale_source_rejected(self):
        self.path.write_bytes(self.raw+b'new')
        with self.assertRaises(SourceError):
            prepare_subquestions(self.adapter, self.sha, self.spec)

    def test_invalid_specs_rejected(self):
        self.spec['questions'][1]['id']='a'
        with self.assertRaises(SourceError):prepare_subquestions(self.adapter,self.sha,self.spec)
        self.spec['questions'][1]['id']='b'
        self.spec['questions'][0]['reference_ranges']=[[0,len(self.raw)+1]]
        with self.assertRaises(SourceError):prepare_subquestions(self.adapter,self.sha,self.spec)
