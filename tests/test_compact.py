import json,unittest
from agora.transform import transform,digest,TransformError

class CompactTests(unittest.TestCase):
    def run_case(self,text,limit):
        source='No publicar. Fecha pendiente.'
        def provider(*args): return {'finish_reason':'stop','content':json.dumps({'claims':[{'text':text,'citations':[{'line':1,'quote':source}]}]})}
        return transform(source.encode(),digest(source.encode()),'s',[1],provider,limit)
    def test_views_link_and_count_rendered_bytes(self):
        r=self.run_case('No publicar; fecha pendiente.',200)
        self.assertEqual(r['structural_status'],'valid')
        self.assertIn('[C1]',r['views']['summary'])
        self.assertEqual(r['views']['evidence']['claims']['C1'][0]['line'],1)
        self.assertEqual(r['summary_budget']['observed_bytes'],len(r['views']['summary'].encode()))
        self.assertEqual(r['review_status'],'unreviewed')
    def test_multibyte_overflow_rejects_without_views(self):
        r=self.run_case('á'*65,128)
        self.assertEqual(r['diagnostic'],'summary_budget_exceeded')
        self.assertNotIn('views',r)
        self.assertNotIn('candidate',r)
        self.assertIn('raw_output',r)
    def test_invalid_budget_never_calls_provider(self):
        with self.assertRaisesRegex(TransformError,'invalid_summary_limit'):
            transform(b'x',digest(b'x'),'s',[],lambda *a:self.fail('called'),True)
    def test_exact_budget_boundary(self):
        r=self.run_case('x'*100,4096)
        size=r['summary_budget']['observed_bytes']
        self.assertEqual(self.run_case('x'*100,size)['structural_status'],'valid')
        self.assertEqual(self.run_case('x'*100,size-1)['structural_status'],'rejected')

if __name__=='__main__': unittest.main()
