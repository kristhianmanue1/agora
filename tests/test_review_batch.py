import copy,json,unittest
from agora.review_batch import review_candidate,ReviewBudget,fingerprint

class ReviewBatchTests(unittest.TestCase):
    def candidate(self,n=3):
        return {'schema':'agora/claim-evidence-query/v2','execution_status':'complete','response_language':'es',
                'prompt':{'user':json.dumps({'question':'Resultados?'})},'requested_aspects':[{'id':'a','question':'Resultados?'}],
                'parts':[{'id':'a','status':'answered','missing':[],'claims':[{'text':f'Caso {i} confirmado.','quotes':[f'Caso {i} confirmado.']} for i in range(n)]}],
                'semantic_support':'not_verified','coverage':'not_verified'}
    def provider(self,s,u,**limits):
        data=json.loads(u);self.assertIn('max_output_tokens',limits);self.assertGreater(limits['timeout_seconds'],0)
        claims=[{'part_id':c['part_id'],'claim_index':c['claim_index'],'relevance':'relevant','details':[{'text':c['text'],'support':'supported','quote_indices':[0],'reason':'Same fact.'}]} for c in data['claims']]
        return {'finish_reason':'stop','content':json.dumps({'language':'match','language_reason':'Spanish.','claims':claims}),'usage':{'total_tokens':100}}
    def test_all_jobs_and_original_indices(self):
        c=self.candidate();before=copy.deepcopy(c);r=review_candidate(c,self.provider)
        self.assertEqual(r['reviewed_jobs'],3);self.assertEqual(r['review_coverage'],'complete');self.assertEqual(r['execution_status'],'complete');self.assertEqual(c,before)
        self.assertEqual([j['claim_index'] for j in r['jobs']],[0,1,2]);self.assertTrue(all(j['review']['assessment']['claims'][0]['claim_index']==0 for j in r['jobs']))
        self.assertEqual(r['recommendation'],'needs_adjudication');self.assertEqual(r['semantic_coverage'],'not_verified');self.assertEqual(r['candidate_sha256'],fingerprint(c))
    def test_call_limit_leaves_unreviewed(self):
        r=review_candidate(self.candidate(),self.provider,budget=ReviewBudget(max_calls=1))
        self.assertEqual(r['ledger']['calls'],1);self.assertEqual(r['review_coverage'],'incomplete');self.assertEqual(r['stop_reason'],'call_budget_exhausted');self.assertEqual(r['jobs'][2]['status'],'not_reviewed')
    def test_output_reservation_never_refunded(self):
        r=review_candidate(self.candidate(),self.provider,budget=ReviewBudget(max_output_tokens_total=8192))
        self.assertEqual(r['ledger']['calls'],1);self.assertEqual(r['ledger']['reserved_output_tokens'],8192);self.assertEqual(r['stop_reason'],'output_budget_exhausted')
    def test_prompt_budget_prevents_call(self):
        r=review_candidate(self.candidate(),lambda *a,**k:self.fail('no call'),budget=ReviewBudget(max_prompt_bytes_total=1))
        self.assertEqual(r['ledger']['calls'],0);self.assertEqual(r['stop_reason'],'prompt_budget_exhausted')
    def test_partial_valid_but_failed_json_never_complete(self):
        calls=[]
        def provider(s,u,**k):
            calls.append(1)
            return dict(self.provider(s,u,**k),content='not json') if len(calls)==2 else self.provider(s,u,**k)
        r=review_candidate(self.candidate(),provider)
        self.assertEqual(len(calls),3);self.assertEqual(r['reviewed_jobs'],2);self.assertEqual(r['execution_status'],'incomplete');self.assertEqual(r['recommendation'],'review_incomplete')
    def test_unknown_usage_stops_without_retry(self):
        def provider(s,u,**k):r=self.provider(s,u,**k);r.pop('usage');return r
        r=review_candidate(self.candidate(),provider)
        self.assertEqual(r['ledger']['calls'],1);self.assertEqual(r['ledger']['unknown_usage_calls'],1);self.assertEqual(r['stop_reason'],'usage_unknown')
    def test_transport_failure_stops(self):
        def provider(*a,**k):raise TimeoutError('test')
        r=review_candidate(self.candidate(),provider)
        self.assertEqual(r['ledger']['calls'],1);self.assertEqual(r['jobs'][0]['status'],'failed');self.assertEqual(r['jobs'][1]['status'],'not_reviewed')
    def test_time_budget_checked_before_dispatch(self):
        times=iter([0,10,10,10]);r=review_candidate(self.candidate(1),lambda *a,**k:self.fail('no call'),clock=lambda:next(times),budget=ReviewBudget(max_seconds=5))
        self.assertEqual(r['ledger']['calls'],0);self.assertEqual(r['stop_reason'],'time_budget_exhausted')
    def test_provider_receives_remaining_timeout(self):
        times=iter([0,8,8,8]);seen=[]
        def provider(s,u,**k):seen.append(k);return self.provider(s,u,**k)
        r=review_candidate(self.candidate(1),provider,clock=lambda:next(times),budget=ReviewBudget(max_seconds=10))
        self.assertEqual(seen[0]['timeout_seconds'],2);self.assertEqual(r['execution_status'],'complete')
    def test_missing_only_part_is_language_review_not_source_coverage(self):
        c=self.candidate(0);c['parts'][0].update(status='not_in_passages',missing=['No consta.'])
        r=review_candidate(c,self.provider);self.assertEqual(r['jobs'][0]['kind'],'missing_only');self.assertEqual(r['reviewed_jobs'],1);self.assertEqual(r['semantic_coverage'],'not_verified')
    def test_duplicate_part_ids_rejected_before_call(self):
        c=self.candidate();c['parts']*=2
        with self.assertRaises(ValueError):review_candidate(c,lambda *a,**k:self.fail('no call'))
    def test_rejected_candidate_not_reviewed(self):
        c=self.candidate();c['execution_status']='rejected'
        with self.assertRaises(ValueError):review_candidate(c,lambda *a,**k:self.fail('no call'))
    def test_snapshots_detached_from_callback(self):
        def callback(r):r['ledger']['calls']=999;r['jobs'].clear()
        r=review_candidate(self.candidate(),self.provider,on_result=callback)
        self.assertEqual(r['ledger']['calls'],3);self.assertEqual(len(r['jobs']),3)
    def test_failed_last_job_not_hidden(self):
        def provider(s,u,**k):
            r=self.provider(s,u,**k)
            if 'Caso 2 confirmado.' in u:r['finish_reason']='length'
            return r
        r=review_candidate(self.candidate(),provider);self.assertEqual(r['reviewed_jobs'],2);self.assertEqual(r['review_coverage'],'incomplete')
    def test_no_reviewer_approval_even_when_supported(self):
        r=review_candidate(self.candidate(),self.provider)
        self.assertEqual(r['adjudication'],'not_performed');self.assertEqual(r['independence'],'not_established')
    def test_invalid_budget_before_dispatch(self):
        with self.assertRaises(ValueError):review_candidate(self.candidate(),self.provider,budget=ReviewBudget(max_calls=True))
    def test_usage_unknown_on_last_call_does_not_approve_complete_coverage(self):
        def provider(s,u,**k):r=self.provider(s,u,**k);r.pop('usage');return r
        r=review_candidate(self.candidate(1),provider)
        self.assertEqual(r['review_coverage'],'complete');self.assertEqual(r['execution_status'],'incomplete');self.assertEqual(r['recommendation'],'review_incomplete')
    def test_late_transport_return_keeps_execution_incomplete(self):
        ticks=iter([0,0,6,6]);r=review_candidate(self.candidate(1),self.provider,clock=lambda:next(ticks),budget=ReviewBudget(max_seconds=5))
        self.assertEqual(r['review_coverage'],'complete');self.assertEqual(r['execution_status'],'incomplete');self.assertEqual(r['stop_reason'],'time_budget_exhausted')
    def test_input_mutation_during_review_does_not_change_snapshot(self):
        c=self.candidate(2);original=fingerprint(c);requests=[]
        def provider(s,u,**k):
            requests.append(json.loads(u));c['parts'][0]['claims'][1]['text']='Changed elsewhere.'
            return self.provider(s,u,**k)
        r=review_candidate(c,provider)
        self.assertEqual(r['candidate_sha256'],original);self.assertEqual(requests[1]['claims'][0]['text'],'Caso 1 confirmado.');self.assertEqual(r['reviewed_jobs'],2)
