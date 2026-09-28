"""Pérdida de respuesta y rollback sin solicitudes remotas."""
import importlib.util
from pathlib import Path
import tempfile
import sqlite3
import unittest
BASE=Path(__file__).resolve().parents[1]/'experiments'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m=load('recovery_test',BASE/'issue-recovery-v1/recovery.py')
f=load('recovery_fixture',BASE/'issue-flow-v1/fixtures.py')
class RecoveryTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'test.db';self.store=m.Store(self.path,create=True)
  self.data,self.raw,source=f.inputs();self.head=self.store.append('nube',None,self.data,self.raw,{'kind':'fixture'})
  self.prepared=m.flow.prepare(self.store,'nube',self.head,source,'2026-10-08');self.calls=0
 def tearDown(self):self.store.close();self.temp.cleanup()
 def provider(self,*args):self.calls+=1;return f.valid_response()
 def test_lost_ack_reopen_and_recover_without_second_call(self):
  result=m.evaluate(self.store,'op1',self.prepared,self.provider)
  self.store.close();self.store=m.Store(self.path)
  recovered=m.evaluate(self.store,'op1',self.prepared,self.provider)
  self.assertEqual(result,recovered);self.assertEqual(self.calls,1);self.assertEqual(len(self.store.history('nube')),2)
 def test_response_ready_resumes_without_provider(self):
  m.reserve(self.store,'op1',self.prepared);m.record_response(self.store,'op1',f.valid_response())
  self.store.close();self.store=m.Store(self.path)
  m.evaluate(self.store,'op1',self.prepared,self.provider)
  self.assertEqual(self.calls,0);self.assertEqual(m.inspect(self.store,'op1')['state'],'committed')
 def test_unknown_outcome_is_not_automatically_resent(self):
  def timeout(*args):self.calls+=1;raise TimeoutError()
  with self.assertRaises(TimeoutError):m.evaluate(self.store,'op1',self.prepared,timeout)
  with self.assertRaisesRegex(ValueError,'provider_outcome_unknown'):m.evaluate(self.store,'op1',self.prepared,self.provider)
  self.assertEqual(self.calls,1);self.assertEqual(len(self.store.history('nube')),1)
 def test_id_reused_for_different_request_rejected(self):
  m.reserve(self.store,'op1',self.prepared)
  altered=dict(self.prepared,sha256='changed')
  with self.assertRaisesRegex(ValueError,'operation_request_conflict'):m.evaluate(self.store,'op1',altered,self.provider)
  self.assertEqual(self.calls,0)
 def test_atomic_revision_and_operation_completion(self):
  m.reserve(self.store,'op1',self.prepared);m.record_response(self.store,'op1',f.valid_response())
  self.store.db.execute("CREATE TRIGGER fail_done BEFORE UPDATE ON operations WHEN json_extract(NEW.payload,'$.state')='committed' BEGIN SELECT RAISE(ABORT,'fixture_failure'); END")
  with self.assertRaises(sqlite3.IntegrityError):m.finalize(self.store,'op1')
  self.assertEqual(len(self.store.history('nube')),1);self.assertEqual(m.inspect(self.store,'op1')['state'],'response_ready')
  self.store.db.execute('DROP TRIGGER fail_done');m.finalize(self.store,'op1')
  self.assertEqual(len(self.store.history('nube')),2)
 def test_concurrent_revision_preserves_response_without_resend(self):
  m.reserve(self.store,'op1',self.prepared);m.record_response(self.store,'op1',f.valid_response())
  self.store.append('nube',self.head,self.data,self.raw,{'kind':'advance'})
  with self.assertRaisesRegex(ValueError,'stale_parent'):m.evaluate(self.store,'op1',self.prepared,self.provider)
  self.assertEqual(self.calls,0);self.assertEqual(m.inspect(self.store,'op1')['state'],'response_ready')
 def test_invalid_response_retained_without_resend(self):
  m.reserve(self.store,'op1',self.prepared);m.record_response(self.store,'op1',dict(f.valid_response(),content='{}'))
  with self.assertRaises(ValueError):m.evaluate(self.store,'op1',self.prepared,self.provider)
  self.assertEqual(self.calls,0);self.assertEqual(len(self.store.history('nube')),1)
 def test_integrity_and_missing_revision(self):
  m.evaluate(self.store,'op1',self.prepared,self.provider)
  self.store.db.execute('DELETE FROM revisions WHERE revision=2')
  with self.assertRaisesRegex(ValueError,'operation_revision_mismatch'):m.inspect(self.store,'op1')
if __name__=='__main__':unittest.main()
