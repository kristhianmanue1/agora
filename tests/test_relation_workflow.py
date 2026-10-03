import hashlib,json,unittest
from agora.relation_candidates import template,FIELDS
from agora.relation_workflow import run

class WorkflowTests(unittest.TestCase):
    raw=b'Atlas translates sentences.'
    def invoke(self,provider,**kw):
        return run(self.raw,'doc',hashlib.sha256(self.raw).hexdigest(),provider,**kw)
    def test_generated_gaps_retained(self):
        c=template(self.raw,'doc');response={'content':json.dumps(c),'finish_reason':'stop'}
        r=self.invoke(lambda s,u:response,question='Atlas?')
        self.assertEqual(r['response'],response);self.assertEqual(r['assessment']['status'],'needs_more_evidence')
        self.assertEqual(r['provider_calls'],1);self.assertFalse(r['admitted'])
    def test_bad_generation_preserved(self):
        response={'content':'{"bad":true}','finish_reason':'stop'}
        r=self.invoke(lambda s,u:response,question='Atlas?')
        self.assertEqual(r['execution_status'],'rejected');self.assertEqual(r['response'],response)
        self.assertNotIn('assessment',r)
    def test_incomplete_and_duplicate_json_rejected(self):
        for response in [{'content':'{}','finish_reason':'length'},{'content':'{"schema":1,"schema":2}','finish_reason':'stop'}]:
            self.assertEqual(self.invoke(lambda s,u:response,question='Atlas?')['execution_status'],'rejected')
    def test_invalid_input_never_calls(self):
        def provider(*args):self.fail('unexpected call')
        r=run(self.raw,'doc','wrong',provider,question='Atlas?')
        self.assertEqual(r['provider_calls'],0)
        self.assertEqual(self.invoke(provider,question='Atlas?',prompt_budget=1)['provider_calls'],0)
        self.assertEqual(self.invoke(provider,candidate={'bad':True})['provider_calls'],0)
    def test_review_inconsistency_is_explicit(self):
        c=template(self.raw,'doc');answers={k:'supported' for k in (*FIELDS,'relation')}
        r=self.invoke(lambda s,u:{'content':json.dumps(answers),'finish_reason':'stop'},candidate=c)
        self.assertEqual(len(r['review_inconsistencies']),6);self.assertEqual(r['review'],answers)
        self.assertFalse(r['admitted']);self.assertEqual(r['next_step'],'explicit_review_required')
    def test_missing_review_and_invalid_choice(self):
        for answers in [{},dict.fromkeys((*FIELDS,'relation'),'approved')]:
            r=self.invoke(lambda s,u:{'content':json.dumps(answers),'finish_reason':'stop'},candidate=template(self.raw,'doc'))
            self.assertEqual(r['execution_status'],'rejected')
    def test_transport_failure_not_retried(self):
        calls=[]
        def failed(*args):calls.append(1);raise TimeoutError()
        r=self.invoke(failed,question='Atlas?')
        self.assertEqual(len(calls),1);self.assertEqual(r['execution_status'],'failed')
