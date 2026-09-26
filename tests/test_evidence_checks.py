import copy,json,unittest
from agora.evidence_review import review_evidence
from agora.review_batch import review_candidate

class CheckedReviewTests(unittest.TestCase):
    def candidate(self):
        return {'schema':'agora/claim-evidence-query/v1','execution_status':'complete','response_language':'en',
                'prompt':{'user':json.dumps({'question':'What does the account report?'})},
                'requested_aspects':[{'id':'a','question':'What does the account report?'}],
                'parts':[{'id':'a','missing':[],'claims':[{'text':'Nera built it.','quotes':['Nera claimed she built it.']}]}]}
    def value(self,**changes):
        d=dict(text='Nera built it.',support='supported',quote_indices=[0],reason='Assessment.',certainty='preserved',scope='same');d.update(changes)
        return {'language':'match','language_reason':'English.','claims':[dict(part_id='a',claim_index=0,relevance='relevant',relevance_reason='Answers the question.',details=[d])]}
    def run_value(self,value,**kwargs):
        return review_evidence(self.candidate(),lambda s,u:dict(content=json.dumps(value),finish_reason='stop'),review_version='v3',**kwargs)
    def test_reported_overstatement_cannot_remain_supported(self):
        r=self.run_value(self.value(certainty='overstated'));c=r['assessment']['claims'][0]
        self.assertEqual(c['support'],'insufficient');self.assertEqual(c['details'][0]['model_support'],'supported');self.assertEqual(r['recommendation'],'needs_revision')
    def test_different_or_unknown_scope_cannot_support_or_contradict(self):
        for scope in ('different','uncertain'):
            for status in ('supported','contradicted'):
                with self.subTest(scope=scope,status=status):
                    c=self.run_value(self.value(scope=scope,support=status))['assessment']['claims'][0]
                    self.assertEqual(c['support'],'insufficient')
    def test_same_scope_contradiction_survives_missing_exception(self):
        r=self.run_value(self.value(support='contradicted',certainty='overstated'))
        self.assertEqual(r['assessment']['claims'][0]['support'],'contradicted')
    def test_missing_quote_not_excused_by_downgrade(self):
        self.assertEqual(self.run_value(self.value(scope='different',quote_indices=[]))['execution_status'],'rejected')
    def test_unrecognized_extra_field_is_not_stripped(self):
        v=self.value();v['claims'][0]['reason_note']='extra'
        self.assertEqual(self.run_value(v)['execution_status'],'rejected')
    def test_missing_check_and_invalid_check_rejected(self):
        v=self.value();del v['claims'][0]['details'][0]['certainty']
        self.assertEqual(self.run_value(v)['execution_status'],'rejected')
        self.assertEqual(self.run_value(self.value(scope=True))['execution_status'],'rejected')
    def test_wrong_model_checks_do_not_prove_truth(self):
        r=self.run_value(self.value())
        self.assertEqual(r['recommendation'],'needs_adjudication')
        self.assertEqual(r['independence'],'not_established')
        self.assertEqual(r['assessment']['claims'][0]['checks_provenance'],'model_reported_not_independently_verified')
    def test_relevance_and_support_are_independent(self):
        r=self.run_value(self.value(support='insufficient',quote_indices=[],scope='uncertain'))
        c=r['assessment']['claims'][0];self.assertEqual(c['relevance'],'relevant');self.assertEqual(c['support'],'insufficient')
    def test_no_input_mutation(self):
        c=self.candidate();before=copy.deepcopy(c);v=self.value(certainty='overstated')
        review_evidence(c,lambda s,u:dict(content=json.dumps(v),finish_reason='stop'),review_version='v3')
        self.assertEqual(c,before)
    def test_bounded_reviewer_selects_v3_and_preserves_budget(self):
        r=review_candidate(self.candidate(),lambda s,u,**kw:dict(content=json.dumps(self.value(certainty='overstated')),finish_reason='stop',usage={'total_tokens':10}),review_version='v3')
        self.assertEqual(r['review_version'],'v3');self.assertEqual(r['ledger']['calls'],1);self.assertEqual(r['recommendation'],'needs_revision')
    def test_unknown_batch_version_never_dispatches(self):
        with self.assertRaises(ValueError):review_candidate(self.candidate(),lambda *a,**k:self.fail('no dispatch'),review_version='invalid')
