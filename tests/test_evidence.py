import json,tempfile,unittest
from pathlib import Path
from agora.evidence import EvidencePolicy,validate_claims,query_evidence,system_prompt
from agora.source import FileSourceAdapter,digest

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.text='Atlas reached 91%. Boreal was not evaluated.'
        self.env={'spans':[{'text':self.text,'start_byte':0}]}
    def response(self,quotes=None,text='Atlas reached 91%.',status='answered',missing=None):
        return {'finish_reason':'stop','content':json.dumps({'parts':[{'id':'a','status':status,'claims':[{'text':text,'quotes':quotes or ['Atlas reached 91%.']}],'missing':missing or []}]})}
    def codes(self,r,policy=None):return [e['code'] for e in validate_claims(r,self.env,['a'],policy or EvidencePolicy())[1]]
    def test_valid_anchor(self):
        p,e,a=validate_claims(self.response(),self.env,['a'],EvidencePolicy());self.assertEqual(e,[]);self.assertEqual(a[0]['matches'],[{'start_byte':0,'end_byte':18}])
    def test_collects_count_duplicate_and_literal_errors(self):
        codes=self.codes(self.response(['Atlas reached 91%.']*12+['Boreal reached 91%.']))
        self.assertIn('quote_count_exceeded',codes);self.assertIn('duplicate_quote_in_claim',codes);self.assertIn('quote_not_literal',codes)
    def test_12_13_boundary_without_duplicate_confound(self):
        text=' '.join(f'Fact {i}.' for i in range(13));self.env={'spans':[{'text':text,'start_byte':0}]}
        self.assertEqual(self.codes(self.response([f'Fact {i}.' for i in range(12)])),[])
        self.assertEqual(self.codes(self.response([f'Fact {i}.' for i in range(13)])),['quote_count_exceeded'])
    def test_configurable_count(self):
        self.env={'spans':[{'text':'A B C','start_byte':0}]}
        self.assertIn('quote_count_exceeded',self.codes(self.response(['A','B','C']),EvidencePolicy(2)))
    def test_utf8_budget_exact_and_one_less(self):
        self.env={'spans':[{'text':'á','start_byte':0}]};r=self.response(['á'])
        self.assertEqual(self.codes(r,EvidencePolicy(12,2,2)),[])
        self.assertEqual(set(self.codes(r,EvidencePolicy(12,1,1))),{'part_quote_bytes_exceeded','total_quote_bytes_exceeded'})
    def test_omitted_aspect_rejected(self):
        _,e,_=validate_claims(self.response(),self.env,['a','b'],EvidencePolicy());self.assertTrue(e)
    def test_partial_requires_gap(self):self.assertIn('status_content_mismatch',self.codes(self.response(status='partial')))
    def test_partial_with_gap(self):self.assertEqual(self.codes(self.response(status='partial',missing=['Boreal accuracy unknown'])),[])
    def test_no_quote_crossing_passages(self):
        self.env={'spans':[{'text':'Atlas','start_byte':0},{'text':'91%','start_byte':20}]}
        self.assertIn('quote_not_literal',self.codes(self.response(['Atlas\n91%'])))
    def test_invalid_policy(self):
        for x in (0,97,True):
            with self.assertRaises(ValueError):EvidencePolicy(x).validate()
    def test_prompt_tracks_policy(self):self.assertIn('At most 7 quote',system_prompt(EvidencePolicy(7)))
    def test_false_claim_remains_unverified(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'source';p.write_text(self.text);a=FileSourceAdapter(p,'test')
            r=query_evidence(a,digest(p.read_bytes()),'Boreal?', [{'id':'a','question':'Boreal?'}],lambda *_:self.response(text='Boreal reached 91%.'))
            self.assertEqual(r['execution_status'],'complete');self.assertEqual(r['semantic_support'],'not_verified');self.assertEqual(r['review_queue'][0]['support'],'not_verified');self.assertEqual(r['coverage'],'not_verified')
    def test_refuses_before_provider_when_prompt_budget_exceeded(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'source';p.write_text(self.text);a=FileSourceAdapter(p,'test')
            def provider(*_):self.fail('provider must not run')
            r=query_evidence(a,digest(p.read_bytes()),'test',[{'id':'a','question':'test'}],provider,prompt_budget=1)
            self.assertEqual(r['execution_status'],'rejected');self.assertEqual(r['provider_calls'],0)
    def test_duplicate_json_keys(self):
        self.assertEqual(self.codes({'finish_reason':'stop','content':'{"parts":[],"parts":[]}'}),['invalid_json'])

    def test_total_budget_across_parts(self):
        value=json.loads(self.response(['Atlas reached 91%.'])['content'])
        second=dict(value['parts'][0],id='b');value['parts'].append(second)
        _,errors,_=validate_claims({'finish_reason':'stop','content':json.dumps(value)},self.env,['a','b'],EvidencePolicy(12,18,35))
        self.assertEqual([e['code'] for e in errors],['total_quote_bytes_exceeded'])

    def test_utf8_anchor_at_nonzero_offset(self):
        env={'spans':[{'text':'á Z','start_byte':10}]}
        _,errors,anchors=validate_claims(self.response(['Z']),env,['a'],EvidencePolicy())
        self.assertEqual(errors,[]);self.assertEqual(anchors[0]['matches'],[{'start_byte':13,'end_byte':14}])

    def test_unclosed_missing_array_is_not_repaired(self):
        r={'finish_reason':'stop','content':'{"parts":[{"id":"a","status":"partial","claims":[],"missing":["not established"}]}'}
        self.assertEqual(self.codes(r),['invalid_json'])

    def test_valid_abstention(self):
        r={'finish_reason':'stop','content':json.dumps({'parts':[{'id':'a','status':'not_in_passages','claims':[],'missing':['No accuracy supplied for Boreal.']}]})}
        self.assertEqual(self.codes(r),[])
