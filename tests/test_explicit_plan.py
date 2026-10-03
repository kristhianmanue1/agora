import json
import tempfile
import unittest
from pathlib import Path
from agora.explicit_plan import prepare
from agora.plan_generation import generate
from agora.source import FileSourceAdapter, digest

class ExplicitPlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'source.txt';self.raw='Dato á: INLINEFORM0.\n\nOtro párrafo.'.encode();self.path.write_bytes(self.raw)
        self.adapter=FileSourceAdapter(self.path,'fixture');self.question='¿Qué se conoce?'
        self.end=self.raw.index(b'\n\n');self.plan=prepare(self.adapter,digest(self.raw),self.question,[[0,self.end]],100)
        self.calls=0
    def provider(self,system,user):
        self.calls+=1;u=json.loads(user)['evidence_units'][0]
        return dict(finish_reason='stop',content=json.dumps({'parts':[dict(id='P1',status='partial',claims=[dict(text='Hay un marcador.',evidence_ids=[u['id']])],missing=['Valor desconocido.'])]}))
    def execute(self,plan=None,question=None):
        raw=json.dumps(plan or self.plan).encode()
        return generate(self.path,raw,digest(raw),question or self.question,self.provider,'ids')
    def test_replay_preserves_source_scope_and_missing(self):
        r=self.execute();self.assertEqual(r['execution_status'],'complete')
        self.assertEqual(r['answer_status'],'candidate_requires_expansion')
        self.assertEqual(r['missing'],['Valor desconocido.']);self.assertFalse(r['selection_verified'])
        self.assertEqual(r['semantic_support'],'not_verified');self.assertEqual(self.calls,1)
        for c in r['citations']:
            m=c['matches'][0];self.assertEqual(self.raw[m['start_byte']:m['end_byte']].decode(),c['quote'])
    def test_changed_question_is_rejected_before_provider(self):
        with self.assertRaisesRegex(ValueError,'plan_question_mismatch'):self.execute(question='Otra pregunta')
        self.assertEqual(self.calls,0)
    def test_changed_source_is_rejected_before_provider(self):
        self.path.write_bytes(b'changed')
        with self.assertRaises(ValueError):self.execute()
        self.assertEqual(self.calls,0)
    def test_modified_plan_even_with_recomputed_hash_is_rejected(self):
        for key,value in [('selection_verified',True),('question','Otra'),('budget_bytes',1)]:
            with self.subTest(key=key):
                p=json.loads(json.dumps(self.plan));p[key]=value
                with self.assertRaises(ValueError):self.execute(p)
        self.assertEqual(self.calls,0)
    def test_invalid_utf8_boundaries_and_budget_rejected(self):
        a=self.raw.index('á'.encode())
        for ranges,budget in [([[a,a+1]],100),([[0,self.end]],1)]:
            with self.assertRaises(ValueError):prepare(self.adapter,digest(self.raw),self.question,ranges,budget)
    def test_wrong_plan_hash_rejected_before_provider(self):
        with self.assertRaisesRegex(ValueError,'plan_hash_or_size_mismatch'):
            generate(self.path,json.dumps(self.plan).encode(),'0'*64,self.question,self.provider,'ids')
        self.assertEqual(self.calls,0)
