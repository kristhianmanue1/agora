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
m=load('repair_store_tests',ROOT/'experiments/repair-store-v1/store.py')
f=load('repair_fixtures',ROOT/'experiments/issue-flow-v4/fixtures.py')
class RepairStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.source_path=Path(self.tmp.name)/'source';self.source=m.flow.Store(self.source_path,create=True);self.addCleanup(self.source.close)
        self.head,source=f.seed(self.source)
        self.prepared=m.flow.flow.prepare(self.source,'nube',self.head,source,'2026-10-09')
        m.flow.reserve(self.source,'original',self.prepared)
        response=json.loads((ROOT/'experiments/issue-flow-v4/result-glm-01.json').read_text())['original_response']
        m.flow.record_response(self.source,'original',response)
        self.snapshot=m.capture(self.source,'original',self.head)
        self.receipt=m.repair.propose(response['content'])
        self.path=Path(self.tmp.name)/'derived';self.store=m.Store(self.path,create=True);self.addCleanup(self.store.close)
    def test_roundtrip_and_repeat_one_record(self):
        result=self.store.put('repair',self.snapshot,self.receipt)
        other=m.Store(self.path)
        try:
            self.assertEqual(other.get('repair',result['digest']),result)
            self.assertEqual(other.put('repair',self.snapshot,self.receipt),result)
            self.assertEqual(other.db.execute('SELECT count(*) FROM derivations').fetchone()[0],1)
        finally:other.close()
        self.assertEqual(m.flow.inspect(self.source,'original')['state'],'response_ready')
        self.assertEqual(len(self.source.history('nube')),1)
    def test_receipt_from_different_response_rejected(self):
        wrong=m.repair.propose(self.receipt['original_content'].replace('Lina','Otra'))
        with self.assertRaisesRegex(ValueError,'repair_response_mismatch'):self.store.put('repair',self.snapshot,wrong)
        self.assertIsNone(self.store.get('repair'))
    def test_changed_values_with_recomputed_hash_rejected(self):
        wrong=copy.deepcopy(self.receipt);wrong['candidate_content']=wrong['candidate_content'].replace('Lina','Otra');wrong['candidate_sha256']=m.repair.sha(wrong['candidate_content'])
        with self.assertRaisesRegex(ValueError,'receipt_mismatch'):self.store.put('repair',self.snapshot,wrong)
    def test_stale_origin_head_rejected(self):
        m.flow.evaluate(self.source,'other',self.prepared,f.provider)
        with self.assertRaisesRegex(ValueError,'head_mismatch'):m.capture(self.source,'original',self.head)
    def test_tampered_request_even_rehashed_rejected(self):
        snapshot=copy.deepcopy(self.snapshot);op=snapshot['operation'];op['request']['provider']['messages'][0]['content']='changed';op['request_hash']=m.digest(op['request'])
        with self.assertRaisesRegex(ValueError,'request_binding'):self.store.put('repair',snapshot,self.receipt)
    def test_incomplete_response_rejected(self):
        s=copy.deepcopy(self.snapshot);s['operation']['response']['finish_reason']='length'
        with self.assertRaisesRegex(ValueError,'incomplete_response'):self.store.put('repair',s,self.receipt)
    def test_failed_insert_rolls_back(self):
        self.store.db.execute("CREATE TRIGGER fail BEFORE INSERT ON derivations BEGIN SELECT RAISE(ABORT,'fixture'); END;")
        with self.assertRaises(sqlite3.IntegrityError):self.store.put('repair',self.snapshot,self.receipt)
        self.assertFalse(self.store.db.in_transaction);self.assertIsNone(self.store.get('repair'))
    def test_same_identity_different_origin_rejected(self):
        self.store.put('repair',self.snapshot,self.receipt)
        s=copy.deepcopy(self.snapshot);s['operation']['id']='another'
        with self.assertRaisesRegex(ValueError,'derivation_request_conflict'):self.store.put('repair',s,self.receipt)
    def test_wrong_external_digest_rejected(self):
        self.store.put('repair',self.snapshot,self.receipt)
        with self.assertRaisesRegex(ValueError,'derivation_integrity'):self.store.get('repair','0'*64)
    def test_foreign_store_rejected_unchanged(self):
        before=self.source_path.read_bytes()
        with self.assertRaisesRegex(ValueError,'incompatible_store'):m.Store(self.source_path)
        self.assertEqual(before,self.source_path.read_bytes())
    def test_stored_payload_tampering_rejected(self):
        self.store.put('repair',self.snapshot,self.receipt)
        self.store.db.execute("UPDATE derivations SET payload=replace(payload,'Lina','Otra')")
        with self.assertRaisesRegex(ValueError,'derivation_integrity'):self.store.get('repair')
