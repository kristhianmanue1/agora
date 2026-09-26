import json
from pathlib import Path
import tempfile
import unittest
from agora.source import FileSourceAdapter, digest, encode_record
from agora.coverage import assess_with_coverage


class CoverageTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name)/'source.txt'
        self.path.write_bytes(b'Phase one.\n\nPhase two.\n')
        self.sha = digest(self.path.read_bytes())
        self.adapter = FileSourceAdapter(self.path, 'coverage-fixture')
        self.calls = 0

    def provider(self, *args):
        self.calls += 1
        return {'finish_reason':'stop', 'content':json.dumps({
            'decision':'sufficient', 'explanation':'Ambas fases presentes.',
            'quotes':['Phase one.'], 'missing':[]})}

    def run_case(self, ranges, scope='global', change=None):
        envelope = self.adapter.fetch(self.sha, ranges)
        if change: envelope.update(change)
        data = encode_record(envelope)
        return assess_with_coverage(self.adapter, self.sha, 'Todas las fases',
            data, digest(data), self.provider, scope=scope)

    def test_global_gap_blocks_even_always_sufficient_provider(self):
        r=self.run_case([(0,10)])
        self.assertEqual(r['global_review_status'],'blocked_incomplete_context')
        self.assertEqual(r['coverage_check']['missing_ranges'],[[10,23]])
        self.assertEqual(self.calls,0)
        self.assertNotIn('judgment',r)

    def test_full_source_allows_judgment_without_certifying_truth(self):
        r=self.run_case([(0,23)])
        self.assertEqual(self.calls,1)
        self.assertEqual(r['judgment']['decision'],'sufficient')
        self.assertEqual(r['global_completeness'],'not_established')
        self.assertEqual(r['semantic_verification'],'not_performed')
        self.assertEqual(r['action_taken'],'none')

    def test_contiguous_fragments_count_as_full(self):
        r=self.run_case([(0,10),(10,23)])
        self.assertEqual(r['coverage_check']['status'],'full')
        self.assertEqual(self.calls,1)

    def test_whitespace_gap_is_conservatively_missing(self):
        r=self.run_case([(0,10),(12,23)])
        self.assertEqual(r['coverage_check']['missing_bytes'],2)
        self.assertEqual(self.calls,0)

    def test_local_partial_stays_limited_to_local_scope(self):
        r=self.run_case([(0,10)],scope='local')
        self.assertEqual(self.calls,1)
        self.assertEqual(r['global_review_status'],'not_requested')
        self.assertEqual(r['coverage_check']['status'],'partial')
        self.assertEqual(r['global_completeness'],'not_established')

    def test_forged_full_coverage_rejected_before_model(self):
        r=self.run_case([(0,10)],change={'coverage':'full'})
        self.assertEqual(r['execution_status'],'rejected')
        self.assertEqual(self.calls,0)

    def test_invalid_scope_rejected_before_model(self):
        r=self.run_case([(0,23)],scope='automatic')
        self.assertEqual(r['diagnostic'],'invalid_coverage_scope')
        self.assertEqual(self.calls,0)

    def test_changed_source_revision_rejected(self):
        envelope=self.adapter.fetch(self.sha,[(0,23)])
        data=encode_record(envelope)
        self.path.write_bytes(b'new source')
        r=assess_with_coverage(self.adapter,self.sha,'All',data,digest(data),
                               self.provider,scope='global')
        self.assertEqual(r['execution_status'],'rejected')
        self.assertEqual(self.calls,0)

    def test_full_coverage_does_not_override_model_failure(self):
        data=encode_record(self.adapter.fetch(self.sha,[(0,23)]))
        r=assess_with_coverage(self.adapter,self.sha,'All',data,digest(data),
                               lambda *args:{'finish_reason':'length'},scope='global')
        self.assertEqual(r['execution_status'],'rejected')
        self.assertEqual(r['global_completeness'],'not_established')

if __name__=='__main__':unittest.main()
