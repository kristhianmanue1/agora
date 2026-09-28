import copy
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m=load('issue_store_v4',ROOT/'experiments/issue-store-v2/store.py')
class IssueStoreV4Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'store.sqlite3';self.store=m.Store(self.path,create=True);self.addCleanup(self.store.close)
        self.case=json.loads((ROOT/'experiments/open-issues-v4/replay-fixtures.json').read_text())[0]
        self.data=self.case['input'];self.raw=self.case['original_content']
        self.candidate=m.encode(m.protocol.prepare_candidate(self.raw,self.data))
    def append(self,head=None):return self.store.append('nube',head,self.data,self.raw,self.candidate,{'kind':'test'})
    def test_roundtrip_preserves_original_and_scope(self):
        head=self.append();other=m.Store(self.path)
        try:
            r=other.history('nube',head)[0]['record']
            self.assertEqual(r['model_content'],self.raw)
            self.assertEqual(r['candidate_content'],self.candidate)
            self.assertEqual(r['assessment']['reviewed_scope'],json.loads(self.candidate)['reviewed_scope'])
            self.assertEqual(r['admission'],'not_admitted')
        finally:other.close()
    def test_changed_model_field_in_candidate_rejected_without_write(self):
        c=json.loads(self.candidate);c['fields']['owner']['observed_value']='Otro'
        with self.assertRaisesRegex(ValueError,'adaptation_mismatch'):
            self.store.append('nube',None,self.data,self.raw,m.encode(c),{'kind':'test'})
        self.assertEqual(self.store.history('nube'),[])
    def test_legacy_databases_rejected_unchanged(self):
        for name in ('issue-store-v1','issue-recovery-v1'):
            with self.subTest(name=name):
                old=load('old_'+name,ROOT/'experiments'/name/'store.py')
                path=Path(self.temp.name)/(name+'.sqlite3');s=old.Store(path,create=True);s.close();before=path.read_bytes()
                with self.assertRaisesRegex(ValueError,'incompatible_store'):m.Store(path)
                self.assertEqual(path.read_bytes(),before)
    def test_existing_file_not_overwritten_or_missing_created(self):
        before=self.path.read_bytes()
        with self.assertRaises(FileExistsError):m.Store(self.path,create=True)
        self.assertEqual(before,self.path.read_bytes())
        path=Path(self.temp.name)/'missing'
        with self.assertRaises(sqlite3.OperationalError):m.Store(path)
        self.assertFalse(path.exists())
    def test_second_writer_stale_head_rejected(self):
        head=self.append();other=m.Store(self.path)
        try:
            self.append(head)
            with self.assertRaisesRegex(ValueError,'stale_parent'):
                other.append('nube',head,self.data,self.raw,self.candidate,{'kind':'test'})
            self.assertEqual(len(other.history('nube')),2)
        finally:other.close()
    def test_transaction_failure_leaves_no_revision(self):
        self.store.db.execute("CREATE TRIGGER reject_insert BEFORE INSERT ON revisions BEGIN SELECT RAISE(ABORT,'fixture'); END;")
        with self.assertRaises(sqlite3.IntegrityError):self.append()
        self.assertFalse(self.store.db.in_transaction)
        self.assertEqual(self.store.history('nube'),[])
    def test_payload_tampering_rejected(self):
        self.append();self.store.db.execute("UPDATE revisions SET payload=replace(payload,'Lina','Otro')")
        with self.assertRaisesRegex(ValueError,'history_integrity'):self.store.history('nube')
    def test_validator_drift_rejected_even_with_recomputed_record_hash(self):
        self.append();record=self.store.history('nube')[0]['record']
        record['validator_manifest']['open-issues-v4/protocol.py']='0'*64
        self.store.db.execute('UPDATE revisions SET digest=?,payload=?',(m.digest(record),m.encode(record)))
        with self.assertRaisesRegex(ValueError,'validator_changed'):self.store.history('nube')
    def test_external_head_detects_deleted_tail(self):
        head=self.append();last=self.append(head)
        self.store.db.execute('DELETE FROM revisions WHERE revision=2')
        with self.assertRaisesRegex(ValueError,'head_mismatch'):self.store.history('nube',last)
    def test_issue_definition_cannot_change(self):
        head=self.append();data=copy.deepcopy(self.data);data['question']='Otra pregunta'
        candidate=m.encode(m.protocol.prepare_candidate(self.raw,data))
        with self.assertRaisesRegex(ValueError,'issue_definition_changed'):
            self.store.append('nube',head,data,self.raw,candidate,{'kind':'test'})
        self.assertEqual(len(self.store.history('nube',head)),1)
