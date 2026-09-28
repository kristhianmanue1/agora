import copy
import importlib.util
from pathlib import Path
import sqlite3
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'experiments/issue-flow-v4'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m=load('flow_v4_recovery',BASE/'recovery.py');fixtures=load('flow_v4_fixtures',BASE/'fixtures.py')
class FlowV4Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'db';self.store=m.Store(self.path,create=True);self.addCleanup(self.store.close)
        self.head,self.source=fixtures.seed(self.store)
        self.prepared=m.flow.prepare(self.store,'nube',self.head,self.source,'2026-10-09')
    def forbidden(self,*args):raise AssertionError('provider_called')
    def test_success_then_replay_without_call(self):
        r=m.evaluate(self.store,'op',self.prepared,fixtures.provider)
        other=m.Store(self.path)
        try:self.assertEqual(m.evaluate(other,'op',self.prepared,self.forbidden),r)
        finally:other.close()
        self.assertEqual(len(self.store.history('nube')),2)
    def test_timeout_preserved_unknown_no_resend(self):
        def timeout(request):raise TimeoutError('simulated')
        with self.assertRaises(TimeoutError):m.evaluate(self.store,'op',self.prepared,timeout)
        self.assertEqual(m.inspect(self.store,'op')['state'],'attempted')
        with self.assertRaisesRegex(ValueError,'provider_outcome_unknown'):m.evaluate(self.store,'op',self.prepared,self.forbidden)
        self.assertEqual(len(self.store.history('nube')),1)
    def test_response_ready_resumes_without_call(self):
        op,_=m.reserve(self.store,'op',self.prepared)
        m.record_response(self.store,'op',fixtures.provider(op['request']['provider']))
        other=m.Store(self.path)
        try:r=m.evaluate(other,'op',self.prepared,self.forbidden)
        finally:other.close()
        self.assertEqual(r['assessment']['status'],'resolved')
    def test_bad_response_preserved_without_revision(self):
        def invalid(request):return dict(content='{}',finish_reason='stop',usage={'total_tokens':0})
        with self.assertRaises(ValueError):m.evaluate(self.store,'op',self.prepared,invalid)
        self.assertEqual(m.inspect(self.store,'op')['state'],'response_ready')
        with self.assertRaises(ValueError):m.evaluate(self.store,'op',self.prepared,self.forbidden)
        self.assertEqual(len(self.store.history('nube')),1)
    def test_stale_preparation_rejected_before_call(self):
        m.evaluate(self.store,'first',self.prepared,fixtures.provider)
        with self.assertRaisesRegex(ValueError,'head_mismatch'):m.evaluate(self.store,'second',self.prepared,self.forbidden)
        self.assertIsNone(m.inspect(self.store,'second'))
    def test_concurrent_writer_blocks_append_but_retains_response(self):
        def provider(request):
            other=m.Store(self.path)
            try:m.evaluate(other,'other',self.prepared,fixtures.provider)
            finally:other.close()
            return fixtures.provider(request)
        with self.assertRaisesRegex(ValueError,'stale_parent'):m.evaluate(self.store,'op',self.prepared,provider)
        self.assertEqual(m.inspect(self.store,'op')['state'],'response_ready')
        self.assertEqual(len(self.store.history('nube')),2)
    def test_atomic_finalize_rollback(self):
        op,_=m.reserve(self.store,'op',self.prepared)
        m.record_response(self.store,'op',fixtures.provider(op['request']['provider']))
        self.store.db.execute("CREATE TRIGGER reject_commit BEFORE UPDATE ON operations WHEN instr(NEW.payload,'committed')>0 BEGIN SELECT RAISE(ABORT,'fixture'); END;")
        with self.assertRaises(sqlite3.IntegrityError):m.finalize(self.store,'op')
        self.assertEqual(len(self.store.history('nube')),1)
        self.assertEqual(m.inspect(self.store,'op')['state'],'response_ready')
    def test_same_id_different_request_rejected(self):
        m.reserve(self.store,'op',self.prepared)
        other=copy.deepcopy(self.prepared);other['package']['input']['as_of']='2026-10-10'
        with self.assertRaisesRegex(ValueError,'operation_request_conflict'):m.evaluate(self.store,'op',other,self.forbidden)
    def test_rehashed_tampered_package_rejected(self):
        other=copy.deepcopy(self.prepared);other['package']['input']['question']='Injected'
        other['sha256']=m.digest(other['package'])
        with self.assertRaisesRegex(ValueError,'package_binding'):m.evaluate(self.store,'op',other,self.forbidden)
    def test_full_request_bound_and_provider_mutation_isolated(self):
        def provider(request):
            result=fixtures.provider(request);request['messages'][0]['content']='altered';return result
        m.evaluate(self.store,'op',self.prepared,provider)
        op=m.inspect(self.store,'op');self.assertEqual(op['request']['provider']['messages'][0]['content'],m.SYSTEM)
    def test_unknown_usage_rejected(self):
        def provider(request):
            r=fixtures.provider(request);r['usage']={};return r
        with self.assertRaisesRegex(ValueError,'unknown_usage'):m.evaluate(self.store,'op',self.prepared,provider)
        self.assertEqual(len(self.store.history('nube')),1)
    def test_prior_v4_store_rejected_without_migration(self):
        old=load('old_v4_store',ROOT/'experiments/issue-store-v2/store.py')
        p=Path(self.temp.name)/'old';s=old.Store(p,create=True);s.close();before=p.read_bytes()
        with self.assertRaisesRegex(ValueError,'incompatible_store'):m.Store(p)
        self.assertEqual(before,p.read_bytes())
