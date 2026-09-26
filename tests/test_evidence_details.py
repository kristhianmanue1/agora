import copy,json,unittest
from agora.evidence_review import review_evidence

class DetailReviewTests(unittest.TestCase):
    text='Se evaluaron cinco clases (A1–C1).'
    def candidate(self):
        return {'schema':'agora/claim-evidence-query/v2','execution_status':'complete','response_language':'es',
                'prompt':{'user':json.dumps({'question':'Qué clases se evaluaron?'})},
                'requested_aspects':[{'id':'a','question':'Clases evaluadas'}],
                'semantic_support':'not_verified','parts':[{'id':'a','missing':[],
                'claims':[{'text':self.text,'quotes':['We evaluated five classes.']}]}]}
    def detail(self,text,status='supported',refs=None):
        return {'text':text,'support':status,'quote_indices':([0] if refs is None else refs),'reason':'Detail judgment.'}
    def value(self,details):
        return {'language':'match','language_reason':'Spanish.','claims':[{'part_id':'a','claim_index':0,'relevance':'relevant','details':details}]}
    def review(self,value,candidate=None):
        return review_evidence(candidate or self.candidate(),lambda s,u:{'finish_reason':'stop','content':json.dumps(value)},review_version='v2')
    def test_missing_qualifier_forces_insufficient(self):
        v=self.value([self.detail('Se evaluaron cinco clases'),self.detail('(A1–C1).','insufficient',[])])
        r=self.review(v);self.assertEqual(r['execution_status'],'complete')
        row=r['assessment']['claims'][0];self.assertEqual(row['support'],'insufficient');self.assertEqual(row['unsupported_details'],[1]);self.assertEqual(r['recommendation'],'needs_revision')
    def test_fully_supported_still_needs_adjudication(self):
        r=self.review(self.value([self.detail(self.text)]))
        self.assertEqual(r['recommendation'],'needs_adjudication');self.assertEqual(r['adjudication'],'not_performed')
    def test_omitted_qualifier_rejected(self):
        r=self.review(self.value([self.detail('Se evaluaron cinco clases')]))
        self.assertEqual(r['diagnostics'][0]['code'],'detail_text_coverage_gap')
    def test_internal_omission_rejected(self):
        r=self.review(self.value([self.detail('Se evaluaron'),self.detail('(A1–C1).')]))
        self.assertEqual(r['diagnostics'][0]['code'],'detail_text_coverage_gap')
    def test_paraphrased_detail_rejected(self):
        self.assertEqual(self.review(self.value([self.detail('Cinco clases fueron evaluadas.')]))['execution_status'],'rejected')
    def test_reordered_details_rejected(self):
        self.assertEqual(self.review(self.value([self.detail('(A1–C1).'),self.detail('Se evaluaron cinco clases')]))['execution_status'],'rejected')
    def test_global_label_from_model_rejected(self):
        v=self.value([self.detail(self.text)]);v['claims'][0]['support']='supported'
        self.assertEqual(self.review(v)['diagnostics'][0]['code'],'invalid_claim_review')
    def test_contradiction_dominates_insufficient(self):
        r=self.review(self.value([self.detail('Se evaluaron cinco clases','contradicted'),self.detail('(A1–C1).','insufficient',[])]))
        self.assertEqual(r['assessment']['claims'][0]['support'],'contradicted')
    def test_false_detail_judgment_still_cannot_be_proven_locally(self):
        # Character coverage is not semantic truth: intentionally wrong model labels.
        r=self.review(self.value([self.detail(self.text)]))
        self.assertEqual(r['assessment']['claims'][0]['support'],'supported')
        self.assertEqual(r['independence'],'not_established');self.assertEqual(r['recommendation'],'needs_adjudication')
    def test_no_candidate_mutation(self):
        c=self.candidate();before=copy.deepcopy(c);self.review(self.value([self.detail(self.text)]),c);self.assertEqual(c,before)
    def test_bool_quote_index_rejected(self):
        self.assertEqual(self.review(self.value([self.detail(self.text,refs=[True])]))['diagnostics'][0]['code'],'invalid_review_quote_index')
    def test_nonexistent_quote_rejected(self):
        self.assertEqual(self.review(self.value([self.detail(self.text,refs=[2])]))['diagnostics'][0]['code'],'invalid_review_quote_index')
    def test_supported_requires_evidence(self):
        self.assertEqual(self.review(self.value([self.detail(self.text,refs=[])]))['diagnostics'][0]['code'],'missing_review_evidence')
    def test_empty_details_rejected(self):
        self.assertEqual(self.review(self.value([]))['diagnostics'][0]['code'],'invalid_review_details')
    def test_unknown_version_no_call(self):
        r=review_evidence(self.candidate(),lambda s,u:self.fail('must not call'),review_version='unknown')
        self.assertEqual(r['provider_calls'],0)
    def test_v2_schema_explicit(self):
        self.assertEqual(self.review(self.value([self.detail(self.text)]))['schema'],'agora/evidence-review/v2')
