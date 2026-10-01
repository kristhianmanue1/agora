import json,tempfile,unittest,subprocess,sys
from pathlib import Path
from agora.structured_plan import prepare
from agora.qasper import render
from agora.source import FileSourceAdapter,digest
from agora.subquestions import prepare_subquestions
from agora.plan_generation import generate

class StructuredTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.paper=dict(title='Study',abstract='Overview.',full_text=[dict(section_name='Dataset evaluation',paragraphs=['The dataset is Río.','Evaluation details.']),dict(section_name='Other',paragraphs=['Other details.'])])
        self.raw,_=render(self.paper);self.path=self.root/'source.txt';self.path.write_bytes(self.raw)
        self.adapter=FileSourceAdapter(self.path,'test');self.spec=dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='P1',query='dataset evaluation',reference_ranges=[])])
    def plan(self):return prepare(self.adapter,digest(self.raw),self.spec,self.paper,150,1)
    def test_preserves_baseline_budget_utf8(self):
        p=self.plan();base=prepare_subquestions(self.adapter,digest(self.raw),self.spec,150,1)
        spans=p['envelope']['spans'];self.assertLessEqual(p['delivered_bytes'],150)
        for s in base['envelope']['spans']:self.assertTrue(any(t['start_byte']<=s['start_byte'] and s['end_byte']<=t['end_byte'] for t in spans))
        for s in spans:self.assertEqual(self.raw[s['start_byte']:s['end_byte']].decode(),s['text'])
    def test_structure_must_render_exact_source(self):
        self.paper['title']='Forged'
        with self.assertRaisesRegex(ValueError,'structure_source_mismatch'):self.plan()
    def test_annotations_not_accepted_as_structure(self):
        self.paper['qas']=[]
        with self.assertRaisesRegex(ValueError,'invalid_source_structure'):self.plan()
    def test_consumer_reconstructs_and_rejects_tampering_before_call(self):
        p=self.plan();calls=[]
        def provider(system,user):
            calls.append(user)
            return dict(finish_reason='stop',content=json.dumps({'parts':[dict(id='P1',status='answer',answer='Río',quotes=['The dataset is Río.'])]}))
        raw=json.dumps(p).encode();result=generate(self.path,raw,digest(raw),'dataset',provider)
        self.assertEqual(result['execution_status'],'complete');self.assertEqual(len(calls),1)
        p['envelope']['spans'][0]['text']='invented';raw=json.dumps(p).encode()
        with self.assertRaises(ValueError):generate(self.path,raw,digest(raw),'dataset',provider)
        self.assertEqual(len(calls),1)
    def test_public_cli_plan_and_generation(self):
        from agora.issue_runtime import ROOT
        cli=[sys.executable,str(ROOT/'scripts/agora_issues.py'),'--workspace',str(self.root/'workspace')]
        def call(args):
            proc=subprocess.run(cli+args,capture_output=True,text=True);self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
        call(['init'])
        structure=self.root/'structure.json';structure.write_text(json.dumps(self.paper));spec=self.root/'spec.json';spec.write_text(json.dumps(self.spec));out=self.root/'plan.json'
        call(['retrieve-structured','--source',str(self.path),'--source-id','test','--source-sha256',digest(self.raw),'--structure',str(structure),'--structure-sha256',digest(structure.read_bytes()),'--spec',str(spec),'--budget','150','--top-k','1','--out',str(out)])
        response=self.root/'response.json';response.write_text(json.dumps(dict(finish_reason='stop',content=json.dumps({'parts':[dict(id='P1',status='answer',answer='Río',quotes=['The dataset is Río.'])]}))))
        call(['generate-plan','--source',str(self.path),'--plan',str(out),'--expected-plan-sha256',digest(out.read_bytes()),'--question','dataset','--response',str(response),'--out',str(self.root/'generation')])
        self.assertEqual(json.loads((self.root/'generation/result.json').read_text())['http_attempts'],0)
