"""Persistencia, recuperación y fallos controlados con SQLite temporal."""
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
BASE=Path(__file__).resolve().parents[1]/'experiments'
spec=importlib.util.spec_from_file_location('issue_store_module',BASE/'issue-store-v1/store.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class IssueStoreTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'test.db'
  case=next(c for c in json.loads((BASE/'open-issues-v3/cases.json').read_text()) if c['id']=='partial_refutation')
  self.data=m.protocol.payload(case,0)
  artifact=json.loads((BASE/'open-issues-v3/result-glm-01.json').read_text())
  r=next(x['result'] for x in artifact['assessments'] if x['case']=='partial_refutation' and x['mode']=='full')
  self.raw=json.dumps(dict(fields=r['fields'],reason=r['reason']))
  self.store=m.Store(self.path,create=True)
 def tearDown(self):
  self.store.close();self.temp.cleanup()
 def append(self,parent=None):return self.store.append('issue',parent,self.data,self.raw,{'kind':'test_replay'})
 def test_reopen_preserves_evidence_and_all_revisions(self):
  a=self.append();b=self.append(a)
  other=m.Store(self.path)
  try:
   h=other.history('issue',b);self.assertEqual(len(h),2);self.assertEqual(h[0]['digest'],a)
   self.assertEqual(h[1]['record']['raw_response'],self.raw);self.assertEqual(h[1]['record']['input'],self.data)
  finally:other.close()
 def test_stale_writer_cannot_overwrite(self):
  other=m.Store(self.path)
  try:
   a=self.append()
   with self.assertRaisesRegex(ValueError,'stale_parent'):other.append('issue',None,self.data,self.raw,{'kind':'stale'})
   self.assertEqual(len(self.store.history('issue',a)),1)
  finally:other.close()
 def test_invalid_candidate_leaves_history_unchanged(self):
  a=self.append()
  with self.assertRaises(ValueError):self.store.append('issue',a,self.data,'{}',{'kind':'bad'})
  self.assertEqual(len(self.store.history('issue',a)),1)
 def test_tampered_payload_is_detected(self):
  self.append();self.store.db.execute("UPDATE revisions SET payload='{}'")
  with self.assertRaisesRegex(ValueError,'history_integrity'):self.store.history('issue')
 def test_tail_removal_detected_with_external_head(self):
  a=self.append();b=self.append(a)
  self.store.db.execute('DELETE FROM revisions WHERE revision=2')
  with self.assertRaisesRegex(ValueError,'head_mismatch'):self.store.history('issue',b)
 def test_failed_insert_rolls_back(self):
  a=self.append();self.store.db.execute("CREATE TRIGGER stop_insert BEFORE INSERT ON revisions BEGIN SELECT RAISE(ABORT, 'fixture_failure'); END")
  with self.assertRaises(sqlite3.IntegrityError):self.append(a)
  self.assertFalse(self.store.db.in_transaction);self.assertEqual(len(self.store.history('issue',a)),1)
 def test_issue_identity_cannot_silently_change(self):
  a=self.append();changed=dict(self.data,question='Otra cuestión distinta')
  with self.assertRaisesRegex(ValueError,'issue_definition_changed'):self.store.append('issue',a,changed,self.raw,{'kind':'changed'})
  self.assertEqual(len(self.store.history('issue',a)),1)
 def test_foreign_database_and_create_overwrite_rejected(self):
  with self.assertRaises(FileExistsError):m.Store(self.path,create=True)
  p=Path(self.temp.name)/'foreign.db';c=sqlite3.connect(p);c.execute('CREATE TABLE other(x)');c.close()
  with self.assertRaisesRegex(ValueError,'foreign_store'):m.Store(p)
if __name__=='__main__':unittest.main()
