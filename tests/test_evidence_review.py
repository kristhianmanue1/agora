import copy,json,tempfile,unittest
from pathlib import Path
from agora.evidence import query_evidence
from agora.evidence_ids import build_units
from agora.evidence_review import review_evidence
from agora.source import FileSourceAdapter,digest

class EvidenceReviewTests(unittest.TestCase):
    def candidate(self):
        return {'schema':'agora/claim-evidence-query/v2','execution_status':'complete','response_language':'es',
          'prompt':{'user':json.dumps({'question':'Resultado de Boreal?'})},'requested_aspects':[{'id':'a','question':'Resultado?'}],
          'semantic_support':'not_verified','parts':[{'id':'a','missing':[],'claims':[{'text':'Boreal obtuvo 91%.','quotes':['Atlas scored 91%.']}]}]}
    def response(self,**changes):
        v={'language':'match','language_reason':'Spanish prose.','claims':[{'part_id':'a','claim_index':0,'support':'insufficient','relevance':'relevant','quote_indices':[],'reason':'Different subject.'}]}
        v.update(changes);return {'finish_reason':'stop','content':json.dumps(v)}
    def test_review_flags_without_mutating_or_promoting(self):
        c=self.candidate();before=copy.deepcopy(c);r=review_evidence(c,lambda s,u:self.response())
        self.assertEqual(c,before);self.assertEqual(r['recommendation'],'needs_revision');self.assertEqual(r['adjudication'],'not_performed')
    def test_positive_still_requires_adjudication(self):
        v=json.loads(self.response()['content']);v['claims'][0].update(support='supported',quote_indices=[0])
        r=review_evidence(self.candidate(),lambda s,u:self.response(**v))
        self.assertEqual(r['recommendation'],'needs_adjudication')
    def test_omitted_claim_rejected(self):
        r=review_evidence(self.candidate(),lambda s,u:self.response(claims=[]))
        self.assertEqual(r['diagnostics'][0]['code'],'incomplete_claim_review')
    def test_fabricated_quote_index_rejected(self):
        v=json.loads(self.response()['content']);v['claims'][0]['quote_indices']=[99]
        r=review_evidence(self.candidate(),lambda s,u:self.response(**v))
        self.assertEqual(r['diagnostics'][0]['code'],'invalid_review_quote_index')
    def test_duplicate_claim_rejected(self):
        v=json.loads(self.response()['content']);v['claims']*=2
        self.assertEqual(review_evidence(self.candidate(),lambda s,u:self.response(**v))['execution_status'],'rejected')
    def test_unknown_language_rejected(self):
        self.assertEqual(review_evidence(self.candidate(),lambda s,u:self.response(language='approved'))['execution_status'],'rejected')
    def test_language_mismatch_flagged(self):
        self.assertEqual(review_evidence(self.candidate(),lambda s,u:self.response(language='mismatch'))['recommendation'],'needs_revision')
    def test_truncated_not_repaired(self):
        r=review_evidence(self.candidate(),lambda s,u:dict(self.response(),finish_reason='length'))
        self.assertEqual(r['diagnostics'][0]['code'],'review_generation_incomplete')
    def test_rejected_candidate_no_call(self):
        c=self.candidate();c['execution_status']='rejected'
        r=review_evidence(c,lambda s,u:self.fail('must not call'));self.assertEqual(r['provider_calls'],0)
    def test_overbudget_no_call(self):
        r=review_evidence(self.candidate(),lambda s,u:self.fail('must not call'),prompt_budget=1)
        self.assertEqual(r['provider_calls'],0)
    def test_whitespace_splits_preserve_offsets_and_all_text(self):
        text='Café with evidence. '*100
        units=build_units({'spans':[{'text':text,'start_byte':12}]},'a','rev',100)
        self.assertEqual(''.join(u['text'] for u in units),text)
        for u in units:self.assertEqual(text.encode()[u['start_byte']-12:u['end_byte']-12].decode(),u['text']);self.assertLessEqual(u['quote_bytes'],100)
    def test_language_and_size_reach_generation(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'s';p.write_text('Evidence. '*100)
            def provider(s,u):
                self.assertIn('every claim text and missing item in English',s)
                units=json.loads(u)['evidence_units'];self.assertTrue(all(x['quote_bytes']<=100 for x in units))
                return {'finish_reason':'stop','content':json.dumps({'parts':[{'id':'a','status':'not_in_passages','claims':[],'missing':['Unknown.']}]})}
            r=query_evidence(FileSourceAdapter(p,'a'),digest(p.read_bytes()),'Question?',[{'id':'a','question':'Question?'}],provider,citation_mode='ids',response_language='en',max_unit_bytes=100)
            self.assertEqual(r['execution_status'],'complete');self.assertEqual(r['language_status'],'not_verified')

    def test_markdown_not_repaired(self):
        r=review_evidence(self.candidate(),lambda s,u:dict(self.response(),content='```json\n'+self.response()['content']+'\n```'))
        self.assertEqual(r['execution_status'],'rejected')
    def test_explicit_empty_language_rejected_without_call(self):
        r=review_evidence(self.candidate(),lambda s,u:self.fail('must not call'),response_language='')
        self.assertEqual(r['provider_calls'],0);self.assertEqual(r['diagnostics'][0]['code'],'invalid_response_language')
    def test_language_and_support_have_separate_outcomes(self):
        v=json.loads(self.response()['content']);v['language']='mismatch';v['claims'][0].update(support='supported',quote_indices=[0])
        r=review_evidence(self.candidate(),lambda s,u:self.response(**v))
        self.assertEqual(r['assessment']['claims'][0]['support'],'supported')
        self.assertEqual(r['recommendation'],'needs_revision')
