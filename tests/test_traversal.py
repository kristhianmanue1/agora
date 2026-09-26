import json
from pathlib import Path
import tempfile
import unittest
from agora.source import FileSourceAdapter,digest
from agora.traversal import walk

class TraversalTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)/'source.txt';self.path.write_bytes(b'First phase. Second phase. Final phase.')
        self.sha=digest(self.path.read_bytes());self.adapter=FileSourceAdapter(self.path,'walk')
    def run_walk(self,provider=None,**opts):
        def extract(s,u):
            text=json.loads(u)['source_window']
            quotes=[q for q in ['First phase.','Second phase.','Final phase.'] if q in text]
            return {'finish_reason':'stop','content':json.dumps({'quotes':quotes})}
        return walk(self.adapter,self.sha,'All phases',provider or extract,unit_bytes=16,**opts)
    def test_full_walk_keeps_last_phase_without_certification(self):
        r=self.run_walk();self.assertEqual(r['traversal_status'],'full')
        self.assertIn('Final phase.',[e['quote'] for e in r['evidence']])
        self.assertEqual(r['semantic_coverage'],'unknown')
        self.assertEqual(r['pending_ranges'],[])
    def test_call_budget_reports_pending(self):
        r=self.run_walk(max_calls=1);self.assertEqual(r['provider_calls'],1)
        self.assertEqual(r['traversal_status'],'partial');self.assertTrue(r['pending_ranges'])
    def test_prompt_budget_prevents_provider(self):
        r=self.run_walk(total_prompt_budget=1);self.assertEqual(r['provider_calls'],0)
        self.assertEqual(r['stop_reason'],'prompt_budget_exhausted')
    def test_retention_budget_does_not_silently_drop_evidence(self):
        r=self.run_walk(retained_budget=1)
        self.assertEqual(r['stop_reason'],'retention_budget_exhausted')
        self.assertEqual(r['traversal_status'],'partial');self.assertEqual(r['evidence'],[])
    def test_nonliteral_quote_fails(self):
        r=self.run_walk(lambda *a:{'finish_reason':'stop','content':'{"quotes":["invented"]}'})
        self.assertEqual(r['execution_status'],'failed');self.assertEqual(r['provider_calls'],1)
    def test_empty_extractions_do_not_establish_semantic_coverage(self):
        r=self.run_walk(lambda *a:{'finish_reason':'stop','content':'{"quotes":[]}'})
        self.assertEqual(r['traversal_status'],'full');self.assertEqual(r['evidence'],[])
        self.assertEqual(r['global_completeness'],'not_established')
    def test_mutation_after_last_call_fails_revision_check(self):
        def provider(*args):
            self.path.write_bytes(b'changed')
            return {'finish_reason':'stop','content':'{"quotes":[]}'}
        r=self.run_walk(provider,max_calls=1)
        self.assertEqual(r['execution_status'],'failed')
        self.assertEqual(r['diagnostic'],'source_revision_mismatch')
    def test_provider_failure_stops_without_retry(self):
        def provider(*args):raise TimeoutError()
        r=self.run_walk(provider);self.assertEqual(r['provider_calls'],1)
        self.assertEqual(r['diagnostic'],'TimeoutError')
    def test_retained_anchors_match_source(self):
        r=self.run_walk();data=self.path.read_bytes()
        for e in r['evidence']:self.assertEqual(data[e['start_byte']:e['end_byte']].decode(),e['quote'])

if __name__=='__main__':unittest.main()
