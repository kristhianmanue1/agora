import json,tempfile,unittest
from pathlib import Path
from agora.source import FileSourceAdapter,digest
from agora.subquestions import prepare_subquestions
from agora.plan_generation import generate

class PlanGenerationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'source.txt';self.raw=b'7.1 Alpha\n\n1. Approve standards.\n'
        self.path.write_bytes(self.raw)
        spec=dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='a',query='Approve',reference_ranges=[])])
        self.plan=prepare_subquestions(FileSourceAdapter(self.path,'x'),digest(self.raw),spec,100,1,'functions-adaptive')
        self.calls=[]
    def provider(self,system,user):
        self.calls.append(user)
        return dict(finish_reason='stop',content=json.dumps({'parts':[dict(id='P1',status='answer',answer='Aprueba normas.',quotes=['Approve standards.'])]}))
    def invoke(self,plan=None):
        data=json.dumps(plan or self.plan).encode();return generate(self.path,data,digest(data),'Función',self.provider)
    def test_live_shape_literal_citation_and_scope(self):
        r=self.invoke();self.assertEqual(r['execution_status'],'complete');self.assertEqual(len(self.calls),1)
        self.assertEqual(r['global_completeness'],'not_established');self.assertEqual(r['semantic_support'],'not_verified')
        self.assertEqual(len(r['citations']),1)
    def test_modified_plan_rejected_before_provider(self):
        self.plan['envelope']['spans'][0]['text']='fake'
        with self.assertRaises(ValueError):self.invoke()
        self.assertFalse(self.calls)
    def test_source_change_rejected(self):
        self.path.write_bytes(self.raw+b'x')
        with self.assertRaises(ValueError):self.invoke()
        self.assertFalse(self.calls)
    def test_wrong_hash_rejected(self):
        with self.assertRaises(ValueError):generate(self.path,json.dumps(self.plan).encode(),'0'*64,'x',self.provider)
        self.assertFalse(self.calls)
    def test_cli_returns_nonzero_for_rejected_saved_response(self):
        import subprocess,sys
        plan=Path(self.tmp.name)/'plan.json';plan.write_text(json.dumps(self.plan))
        response=Path(self.tmp.name)/'response.json';response.write_text(json.dumps(dict(finish_reason='stop',content='{}')))
        workspace=Path(self.tmp.name)/'workspace'
        from agora.issue_runtime import ROOT
        entry=str(ROOT/'scripts/agora_issues.py')
        p=subprocess.run([sys.executable,entry,'--workspace',str(workspace),'init'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0)
        args=[sys.executable,entry,'--workspace',str(workspace),'generate-plan','--source',str(self.path),'--plan',str(plan),'--expected-plan-sha256',digest(plan.read_bytes()),'--question','Función','--response',str(response),'--out',str(Path(self.tmp.name)/'out')]
        p=subprocess.run(args,capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertEqual(json.loads(p.stdout)['status'],'rejected')
        self.assertEqual(json.loads(p.stdout)['http_attempts'],0)
        p=subprocess.run(args,capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
