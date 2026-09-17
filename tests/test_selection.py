import json, unittest
from agora.transform import transform,digest,render_views,snapshot

class SelectionTests(unittest.TestCase):
    def run_case(self,source,text,wrap=lambda x:x):
        payload=json.dumps({'claims':[{'text':text,'citations':[{'line':1,'quote':source.splitlines()[0]}]}]})
        raw=wrap(payload)
        r=transform(source.encode(),digest(source.encode()),'test',[1],lambda *a:{'finish_reason':'stop','content':raw},2800)
        self.assertEqual(r['raw_output'],raw)
        self.assertEqual(r['semantic_support'],'not_verified')
        return r
    def test_longer_candidate_selects_exact_source(self):
        source='No publicar.\r\n'
        r=self.run_case(source,'No se permite publicar.')
        self.assertEqual(r['compression']['status'],'not_shorter')
        self.assertEqual(r['views']['reading'].encode(),source.encode())
        self.assertEqual(r['reading_selection']['kind'],'original_source')
        self.assertIn('candidate',r)
    def test_shorter_candidate_is_still_unreviewed(self):
        r=self.run_case('No publicar. '+('Contexto secundario. '*20),'No publicar.')
        self.assertEqual(r['compression']['status'],'shorter')
        self.assertEqual(r['reading_selection']['kind'],'candidate_summary')
        self.assertFalse(r['reading_selection']['semantic_acceptance'])
        self.assertEqual(r['review_status'],'unreviewed')
    def test_equal_size_is_not_saving(self):
        # Render overhead is part of the criterion, including multibyte text.
        text='á'
        size=len(render_views({'claims':[{'text':text,'citations':[]}]},{'source_id':'x','sha256':'x'})[0].encode())
        r=self.run_case('x'*size,text)
        self.assertEqual(r['compression']['saved_bytes'],0)
        self.assertEqual(r['reading_selection']['kind'],'original_source')
    def test_unpaired_surrogate_rejected_and_raw_preserved(self):
        raw=json.dumps({'claims':[{'text':'\ud800','citations':[{'line':1,'quote':'source'}]}]})
        for limit in (None,2800):
            r=transform(b'source',digest(b'source'),'s',[1],lambda *a:{'finish_reason':'stop','content':raw},limit)
            self.assertEqual(r['structural_status'],'rejected')
            self.assertEqual(r['diagnostic'],'invalid_claim_utf8')
            self.assertEqual(r['raw_output'],raw)
    def test_exact_fence_is_recorded(self):
        r=self.run_case('No publicar.','No publicar.',lambda x:'```json\n'+x+'\n```')
        self.assertEqual(r['structural_status'],'valid')
        self.assertEqual(r['output_normalization']['operation'],'single_json_fence_removed')
    def test_ambiguous_wrappers_rejected(self):
        for wrap in [lambda x:'Comentario\n```json\n'+x+'\n```',lambda x:'```json\n'+x+'\n```\nFin',lambda x:'```json\n'+x+'\n```\n```json\n'+x+'\n```',lambda x:x+x,lambda x:'```python\n'+x+'\n```',lambda x:x.replace('"claims":','"claims":[],"claims":',1)]:
            with self.subTest(wrap=wrap):
                r=self.run_case('No publicar.','No publicar.',wrap)
                self.assertEqual(r['structural_status'],'rejected')
                self.assertNotIn('reading_selection',r)
    def test_fence_does_not_bypass_citation_check(self):
        r=self.run_case('No publicar.','No publicar.',lambda x:'```json\n'+x.replace('"quote": "No publicar."','"quote": "Publicar."')+'\n```')
        self.assertEqual(r['diagnostic'],'quote_mismatch')

if __name__=='__main__':unittest.main()
