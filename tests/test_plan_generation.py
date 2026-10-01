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
    def test_lexical_plan_serialized_roundtrip(self):
        spec=dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='a',query='Approve',reference_ranges=[])])
        self.plan=prepare_subquestions(FileSourceAdapter(self.path,'x'),digest(self.raw),spec,100,1)
        self.assertEqual(self.invoke()['execution_status'],'complete')
        self.plan['questions'][0]['selected_ranges'][0]=(0,1)
        calls=len(self.calls)
        with self.assertRaises(ValueError):self.invoke()
        self.assertEqual(len(self.calls),calls)
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
    def test_ids_resolve_original_offsets(self):
        def provider(system,user):
            units=json.loads(user)['evidence_units']
            return dict(finish_reason='stop',content=json.dumps({'parts':[dict(id='P1',status='answered',claims=[dict(text='Aprueba normas.',evidence_ids=[units[-1]['id']])],missing=[])]}))
        data=json.dumps(self.plan).encode()
        r=generate(self.path,data,digest(data),'Función',provider,'ids')
        self.assertEqual(r['execution_status'],'complete')
        self.assertEqual(r['schema'],'agora/claim-evidence-query/v2')
        for citation in r['citations']:
            anchor=citation['matches'][0]
            self.assertEqual(self.raw[anchor['start_byte']:anchor['end_byte']].decode(),citation['quote'])
        self.assertEqual(r['semantic_support'],'not_verified')
        self.assertEqual(r['global_completeness'],'not_established')
    def test_ids_reject_invented_and_foreign_revision(self):
        from agora.evidence_ids import build_units
        foreign=build_units(self.plan['envelope'],'x','different-revision')[0]['id']
        for uid in ['ev_invented',foreign]:
            def provider(system,user):
                return dict(finish_reason='stop',content=json.dumps({'parts':[dict(id='P1',status='answered',claims=[dict(text='Claim',evidence_ids=[uid])],missing=[])]}))
            data=json.dumps(self.plan).encode();r=generate(self.path,data,digest(data),'Función',provider,'ids')
            self.assertEqual(r['execution_status'],'rejected')
            self.assertEqual(r['diagnostics'][0]['code'],'unknown_evidence_id')
