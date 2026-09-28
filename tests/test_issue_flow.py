"""Controles del adaptador sin red y carrera simulada durante evaluación."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
BASE=Path(__file__).resolve().parents[1]/'experiments/issue-flow-v1'
def load(name):
 spec=importlib.util.spec_from_file_location('flow_test_'+name,BASE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m=load('adapter');f=load('fixtures')
class FlowTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.store=m.Store(Path(self.temp.name)/'test.db',create=True)
  self.data,self.raw,self.source=f.inputs();self.head=self.store.append('nube',None,self.data,self.raw,{'kind':'test'})
 def tearDown(self):self.store.close();self.temp.cleanup()
 def prepare(self):return m.prepare(self.store,'nube',self.head,self.source,'2026-10-08')
 def test_prepare_is_readonly(self):
  p=self.prepare();self.assertEqual(len(self.store.history('nube')),1);self.assertEqual(len(p['package']['input']['sources']),2)
 def test_source_hash_duplicate_and_cutoff(self):
  for source,cutoff in [(dict(self.source,sha256='0'*64),'2026-10-08'),(self.data['sources'][0],'2026-10-08'),(self.source,'2026-10-07')]:
   with self.assertRaises(ValueError):m.prepare(self.store,'nube',self.head,source,cutoff)
 def test_tampered_package_even_with_new_hash(self):
  p=self.prepare();p['package']['input']['question']='Otra pregunta';p['sha256']=m.digest(p['package'])
  with self.assertRaisesRegex(ValueError,'package_binding'):m.check_package(self.store,p)
 def test_stale_before_call_does_not_call_provider(self):
  p=self.prepare();self.store.append('nube',self.head,self.data,self.raw,{'kind':'advance'})
  def provider(*args):self.fail('provider must not be called')
  with self.assertRaises(ValueError):m.evaluate_and_record(self.store,p,provider)
 def test_concurrent_revision_during_call_prevents_append(self):
  p=self.prepare()
  def provider(*args):
   self.store.append('nube',self.head,self.data,self.raw,{'kind':'concurrent'});return f.valid_response()
  with self.assertRaisesRegex(ValueError,'stale_parent'):m.evaluate_and_record(self.store,p,provider)
  self.assertEqual(len(self.store.history('nube')),2)
 def test_invalid_output_and_unknown_usage_leave_base(self):
  for response in [dict(f.valid_response(),content='{}'),dict(f.valid_response(),usage={})]:
   with self.assertRaises(ValueError):m.evaluate_and_record(self.store,self.prepare(),lambda *args:response)
   self.assertEqual(len(self.store.history('nube')),1)
 def test_success_is_candidate_and_replay_rejected(self):
  p=self.prepare();r=m.evaluate_and_record(self.store,p,lambda *args:f.valid_response())
  self.assertEqual(r['admission'],'not_admitted');self.assertEqual(r['assessment']['status'],'resolved')
  with self.assertRaises(ValueError):m.evaluate_and_record(self.store,p,lambda *args:self.fail('no duplicate call'))
  self.assertEqual(len(self.store.history('nube')),2)
if __name__=='__main__':unittest.main()
