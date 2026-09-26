import json
from pathlib import Path
import tempfile
import unittest
from agora.source import FileSourceAdapter, digest, encode_record
from agora.traversal import walk
from agora.routed_query import query_routed


class RoutedQueryTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.path=Path(t.name)/'source.txt'
        self.path.write_text('Inicio: Ada.\n\nCierre: Bruno.\n')
        self.sha=digest(self.path.read_bytes());self.adapter=FileSourceAdapter(self.path,'test')
        self.question='Responsables de inicio y cierre'
        self.parts=[{'id':'start','question':'¿Quién inicia?'},{'id':'end','question':'¿Quién cierra?'}]
        self.calls=0
    def provider(self,system,user):
        self.calls+=1
        return {'finish_reason':'stop','content':json.dumps({'parts':[
            {'id':'start','status':'answer','answer':'Ada','quotes':['Inicio: Ada.']},
            {'id':'end','status':'answer','answer':'Bruno','quotes':['Cierre: Bruno.']}]})}
    def query(self,**kwargs):
        return query_routed(self.adapter,self.sha,self.question,self.parts,kwargs.pop('provider',self.provider),**kwargs)
    def record(self,max_calls=9):
        def extract(s,u):
            text=json.loads(u)['source_window']
            return {'finish_reason':'stop','content':json.dumps({'quotes':[x for x in ['Inicio: Ada.','Cierre: Bruno.'] if x in text]})}
        r=walk(self.adapter,self.sha,self.question,extract,unit_bytes=16,max_calls=max_calls)
        data=encode_record(r);return {'traversal_data':data,'traversal_hash':digest(data)}
    def test_full_source_preferred_even_with_unused_bad_record(self):
        r=self.query(traversal_data=b'invalid',traversal_hash='bad')
        self.assertEqual(r['route'],'full_source');self.assertEqual(self.calls,1)
        self.assertEqual(r['answer_status'],'candidate');self.assertEqual(r['unanswered_parts'],[])
    def test_exact_source_budget_boundary(self):
        size=len(self.path.read_bytes())
        self.assertEqual(self.query(full_source_budget=size)['route'],'full_source')
        self.assertEqual(self.query(full_source_budget=size-1)['answer_status'],'traversal_required')
        self.assertEqual(self.calls,1)
    def test_prompt_overhead_is_counted(self):
        r=self.query(prompt_budget=100)
        self.assertEqual(r['route_reason'],'full_prompt_budget_exceeded');self.assertEqual(self.calls,0)
    def test_verified_record_used_when_direct_budget_exceeded(self):
        r=self.query(full_source_budget=1,**self.record())
        self.assertEqual(r['route'],'verified_traversal');self.assertEqual(self.calls,1)
        self.assertEqual(r['global_completeness'],'not_established')
    def test_partial_record_blocks_with_pending_ranges(self):
        r=self.query(full_source_budget=1,**self.record(max_calls=1))
        self.assertEqual(r['answer_status'],'blocked_partial_traversal')
        self.assertTrue(r['pending_ranges']);self.assertEqual(self.calls,0)
    def test_tampered_record_does_not_call_provider(self):
        r=self.query(full_source_budget=1,traversal_data=b'{}',traversal_hash='bad')
        self.assertEqual(r['execution_status'],'rejected');self.assertEqual(self.calls,0)
    def test_retained_context_also_has_prompt_budget(self):
        r=self.query(full_source_budget=1,prompt_budget=100,**self.record())
        self.assertEqual(r['diagnostic'],'retained_prompt_budget_exceeded');self.assertEqual(self.calls,0)
    def test_missing_response_part_rejected(self):
        def provider(*args):return {'finish_reason':'stop','content':json.dumps({'parts':[{'id':'start','status':'answer','answer':'Ada','quotes':['Inicio: Ada.']}]})}
        r=self.query(provider=provider);self.assertEqual(r['execution_status'],'rejected')
    def test_pending_part_preserves_known_answer(self):
        def provider(*args):return {'finish_reason':'stop','content':json.dumps({'parts':[
            {'id':'start','status':'answer','answer':'Ada','quotes':['Inicio: Ada.']},
            {'id':'end','status':'not_in_document','answer':'','quotes':[]}]})}
        r=self.query(provider=provider)
        self.assertEqual(r['answer_status'],'candidate_partial');self.assertEqual(r['unanswered_parts'],['end'])
        self.assertEqual(r['parts'][0]['answer'],'Ada')
    def test_thirteen_quotes_in_one_part_rejected(self):
        def provider(s,u):
            r=self.provider(s,u);v=json.loads(r['content']);v['parts'][0]['quotes']*=13
            r['content']=json.dumps(v);return r
        self.assertEqual(self.query(provider=provider)['execution_status'],'rejected')
    def test_duplicate_request_ids_rejected_before_call(self):
        self.parts[1]['id']='start'
        self.assertEqual(self.query()['diagnostic'],'duplicate_part_ids');self.assertEqual(self.calls,0)
    def test_citation_cannot_join_separate_retained_passages(self):
        def provider(s,u):
            r=self.provider(s,u);v=json.loads(r['content'])
            v['parts'][0]['quotes']=['Inicio: Ada.\nCierre: Bruno.'];r['content']=json.dumps(v);return r
        r=self.query(full_source_budget=1,provider=provider,**self.record())
        self.assertEqual(r['diagnostic'],'quote_outside_literal_passage')
    def test_source_revision_change_rejected_before_call(self):
        self.path.write_text('Cambiado')
        self.assertEqual(self.query()['execution_status'],'rejected');self.assertEqual(self.calls,0)
    def test_part_omission_can_still_be_semantically_wrong(self):
        def provider(s,u):
            r=self.provider(s,u);v=json.loads(r['content']);v['parts'][0]['answer']='Ada y un supervisor no citado'
            r['content']=json.dumps(v);return r
        r=self.query(provider=provider)
        self.assertEqual(r['execution_status'],'complete')
        self.assertEqual(r['semantic_support'],'not_verified')

    def test_language_default_preserves_spanish_prompt(self):
        from agora.routed_query import SYSTEM
        r=self.query()
        self.assertEqual(r['prompt']['system'],SYSTEM)
        self.assertEqual(r['response_language'],'es')
    def test_english_prompt_and_exact_budget(self):
        r=self.query(response_language='en')
        self.assertIn('in English',r['prompt']['system'])
        self.assertNotIn('in Spanish',r['prompt']['system'])
        self.assertEqual(self.query(response_language='en',prompt_budget=r['prompt_bytes'])['answer_status'],'candidate')
        self.assertEqual(self.query(response_language='en',prompt_budget=r['prompt_bytes']-1)['answer_status'],'traversal_required')
    def test_unknown_language_rejected_without_provider(self):
        self.assertEqual(self.query(response_language='xx')['diagnostic'],'unsupported_response_language')
        self.assertEqual(self.calls,0)
    def test_english_on_traversal_route(self):
        r=self.query(response_language='en',full_source_budget=1,**self.record())
        self.assertEqual(r['route'],'verified_traversal')
        self.assertIn('in English',r['prompt']['system'])

    def concise_provider(self,system,user):
        r=self.provider(system,user);v=json.loads(r['content'])
        for p in v['parts']:p['explanation']='The source explicitly names this person.'
        r['content']=json.dumps(v);return r
    def test_concise_profile_separates_explanation(self):
        r=self.query(answer_profile='concise-v1',provider=self.concise_provider)
        self.assertEqual(r['schema'],'agora/routed-query/v0.3')
        self.assertEqual(r['parts'][0]['answer'],'Ada')
        self.assertTrue(r['parts'][0]['explanation'])
        self.assertEqual(r['semantic_support'],'not_verified')
    def test_concise_missing_explanation_rejected(self):
        r=self.query(answer_profile='concise-v1')
        self.assertEqual(r['execution_status'],'rejected')
    def test_concise_overlong_answer_rejected_not_truncated(self):
        def provider(s,u):
            r=self.concise_provider(s,u);v=json.loads(r['content']);v['parts'][0]['answer']='x'*1001
            r['content']=json.dumps(v);return r
        r=self.query(answer_profile='concise-v1',provider=provider)
        self.assertEqual(r['execution_status'],'rejected')
        self.assertIn('x'*1001,r['response']['content'])
    def test_concise_abstention_has_explanation_but_no_answer(self):
        def provider(s,u):
            r=self.concise_provider(s,u);v=json.loads(r['content'])
            v['parts'][1].update(status='not_in_document',answer='',quotes=[],explanation='The requested role is not established.')
            r['content']=json.dumps(v);return r
        r=self.query(answer_profile='concise-v1',provider=provider)
        self.assertEqual(r['unanswered_parts'],['end'])
        self.assertEqual(r['parts'][1]['answer'],'')
    def test_concise_prompt_budget_and_traversal(self):
        r=self.query(answer_profile='concise-v1',provider=self.concise_provider,full_source_budget=1,**self.record())
        self.assertEqual(r['route'],'verified_traversal')
        count=sum(len(t.encode()) for t in r['prompt'].values())
        self.assertEqual(r['prompt_bytes'],count)
        self.assertEqual(self.query(answer_profile='concise-v1',prompt_budget=100)['answer_status'],'traversal_required')
    def test_unknown_profile_rejected_before_call(self):
        self.assertEqual(self.query(answer_profile='unknown')['diagnostic'],'unsupported_answer_profile')
        self.assertEqual(self.calls,0)
    def test_concise_semantic_error_remains_unverified(self):
        def provider(s,u):
            r=self.concise_provider(s,u);v=json.loads(r['content']);v['parts'][0]['answer']='Someone else'
            r['content']=json.dumps(v);return r
        r=self.query(answer_profile='concise-v1',provider=provider)
        self.assertEqual(r['execution_status'],'complete')
        self.assertEqual(r['semantic_support'],'not_verified')

    def test_concise_abstention_cannot_omit_empty_quotes(self):
        def provider(s,u):
            return {'finish_reason':'stop','content':json.dumps({'parts':[
                {'id':p['id'],'status':'not_in_document','answer':'','explanation':'Missing fact.'} for p in self.parts]})}
        r=self.query(answer_profile='concise-v1',provider=provider)
        self.assertEqual(r['diagnostic'],'invalid_concise_answer_shape')
        self.assertEqual(r['execution_status'],'rejected')

    def test_concise_bare_array_is_rejected(self):
        def provider(s,u):
            r=self.concise_provider(s,u);r['content']=json.dumps(json.loads(r['content'])['parts']);return r
        r=self.query(answer_profile='concise-v1',provider=provider)
        self.assertEqual(r['diagnostic'],'invalid_concise_answer_shape')

if __name__=='__main__':unittest.main()
