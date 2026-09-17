import json, unittest
from agora.query import query,sha
from agora.transform import transform

SOURCE=b'Only synthetic files.\nNo deployment permission.\nNo production evaluation exists.\n'

def fixture():
    payload={'claims':[{'text':'Only synthetic files; no deployment permission.','citations':[{'line':1,'quote':'Only synthetic files.'},{'line':2,'quote':'No deployment permission.'}]}]}
    run=transform(SOURCE,sha(SOURCE),'fixture',[1,2],lambda *a:{'content':json.dumps(payload),'finish_reason':'stop'},2800)
    return json.dumps(run).encode()

def answer(status,text='',quotes=None):
    return {'finish_reason':'stop','content':json.dumps({'parts':[{'id':'P1','status':'answer' if status=='answer' else 'not_in_document','answer':text,'quotes':quotes or []}]})}

class QueryTests(unittest.TestCase):
    def call(self,responses,force=False,source=SOURCE,run=None):
        run=fixture() if run is None else run;calls=[]
        def provider(system,user):
            calls.append(json.loads(user))
            response=responses[len(calls)-1]
            if isinstance(response,Exception):raise response
            return response
        result=query(source,sha(SOURCE),run,sha(run),'Is there production evaluation?',provider,force)
        return result,calls
    def test_missing_summary_recovers_source_without_sharing_prior_answer(self):
        r,c=self.call([answer('needs_source'),answer('answer','No evaluation exists.',['No production evaluation exists.'])])
        self.assertEqual([s['stage'] for s in c],['summary','source'])
        self.assertNotIn('No production evaluation exists.',c[0]['document'])
        self.assertEqual(c[1]['document'],SOURCE.decode())
        self.assertEqual(set(c[1]),{'document','question','stage','parts'})
        self.assertEqual(r['answered_from'],'source')
        self.assertEqual(r['review_status'],'unreviewed')
    def test_summary_document_excludes_presentation_metadata(self):
        r,c=self.call([answer('answer','No deployment.',['no deployment permission.'])])
        self.assertNotIn('Borrador pendiente de revisión.',c[0]['document'])
        self.assertNotIn('[C1]',c[0]['document'])
    def test_summary_answer_uses_one_call(self):
        r,c=self.call([answer('answer','No deployment.',['no deployment permission.'])])
        self.assertEqual(len(c),1);self.assertEqual(r['answered_from'],'summary')
        self.assertEqual(r['retrieval_mode'],'summary_then_source_if_missing_or_multipart')
    def test_unknown_in_source_is_not_false_nonexistence(self):
        r,c=self.call([answer('needs_source'),answer('not_in_source')])
        self.assertEqual(r['answer_status'],'not_in_source');self.assertEqual(r['quotes'],[])
    def test_forced_source_skips_model_routing(self):
        r,c=self.call([answer('not_in_source')],force=True)
        self.assertEqual(len(c),1);self.assertEqual(c[0]['stage'],'source')
    def test_hash_drift_never_calls_model(self):
        r,c=self.call([],source=SOURCE+b'drift')
        self.assertEqual(r['execution_status'],'rejected');self.assertEqual(c,[])
    def test_altered_summary_binding_rejected(self):
        run=json.loads(fixture());run['views']['summary']='Fabricated summary'
        r,c=self.call([],run=json.dumps(run).encode())
        self.assertEqual(r['execution_status'],'rejected');self.assertEqual(c,[])
    def test_inconsistent_original_run_rejected_before_provider(self):
        variants=[('schema','unrelated/v900'),('execution_status','failed'),('raw_output','{"claims":[]}')]
        for key,value in variants:
            run=json.loads(fixture());run[key]=value
            r,c=self.call([],run=json.dumps(run).encode())
            self.assertEqual(r['execution_status'],'rejected');self.assertEqual(c,[])
        run=json.loads(fixture());run['producer']['finish_reason']='length'
        r,c=self.call([],run=json.dumps(run).encode())
        self.assertEqual(r['execution_status'],'rejected');self.assertEqual(c,[])
    def test_bad_quote_stops_without_source_or_retry(self):
        r,c=self.call([answer('answer','Invented.',['Not in document'])])
        self.assertEqual(r['diagnostic'],'answer_quote_mismatch');self.assertEqual(len(c),1)
        self.assertIn('response',r['steps'][0]);self.assertNotIn('answer',r)
    def test_timeout_second_step_preserves_first(self):
        r,c=self.call([answer('needs_source'),TimeoutError('do not echo private detail')])
        self.assertEqual(r['execution_status'],'failed');self.assertEqual(r['diagnostic'],'TimeoutError')
        self.assertEqual(len(c),2);self.assertEqual(r['steps'][0]['parsed_parts'][0]['status'],'not_in_document')
        self.assertNotIn('private detail',json.dumps(r))
    def test_malformed_or_truncated_or_surrogate_rejected(self):
        replies=[{'finish_reason':'length','content':'{}'},answer('needs_source','Unsupported claim'),answer('answer','\ud800',['no deployment permission.']),{'finish_reason':'stop','content':'{"status":"answer","status":"needs_source","answer":"","quotes":[]}'}]
        for reply in replies:
            with self.subTest(reply=reply):
                r,c=self.call([reply]);self.assertEqual(r['execution_status'],'rejected');self.assertEqual(len(c),1)
    def test_semantic_error_can_pass_structure_and_remains_unverified(self):
        r,c=self.call([answer('answer','There is no production evaluation.',['no deployment permission.'])])
        self.assertEqual(r['execution_status'],'complete')
        self.assertEqual(r['answered_from'],'summary');self.assertEqual(len(c),1)
        self.assertEqual(r['semantic_support'],'not_verified')

if __name__=='__main__':unittest.main()
