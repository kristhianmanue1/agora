import json
from pathlib import Path
import tempfile
import unittest
from agora.source import FileSourceAdapter,digest,encode_record
from agora.traversal import walk
from agora.traversal_query import query_traversal

class TraversalQueryTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.path=Path(t.name)/'source.txt';self.path.write_text('Primera fase. Última fase.')
        self.sha=digest(self.path.read_bytes());self.a=FileSourceAdapter(self.path,'source')
        self.calls=0
    def record(self,max_calls=9,empty=False):
        def extract(s,u):
            text=json.loads(u)['source_window']
            return {'finish_reason':'stop','content':json.dumps({'quotes':[] if empty else [q for q in ['Primera fase.','Última fase.'] if q in text]})}
        return walk(self.a,self.sha,'Todas las fases',extract,unit_bytes=16,max_calls=max_calls)
    def query(self,r,question='Todas las fases'):
        data=encode_record(r)
        def answer(*args):
            self.calls+=1
            return {'finish_reason':'stop','content':json.dumps({'parts':[{'id':'P1','status':'answer','answer':'Primera y última fase.','quotes':['Primera fase.','Última fase.']}]})}
        return query_traversal(self.a,self.sha,question,data,digest(data),answer)
    def test_full_traversal_returns_unverified_candidate(self):
        r=self.query(self.record());self.assertEqual(r['answer_status'],'candidate')
        self.assertEqual(self.calls,1);self.assertEqual(r['global_completeness'],'not_established')
    def test_partial_has_pending_and_no_provider(self):
        r=self.query(self.record(max_calls=1))
        self.assertEqual(r['answer_status'],'blocked_partial_traversal')
        self.assertTrue(r['pending_ranges']);self.assertEqual(self.calls,0)
    def test_removed_evidence_cannot_pass_replay(self):
        r=self.record();r['evidence']=[]
        self.assertEqual(self.query(r)['execution_status'],'rejected');self.assertEqual(self.calls,0)
    def test_forged_full_cannot_pass_replay(self):
        r=self.record(max_calls=1);r['traversal_status']='full';r['pending_ranges']=[]
        self.assertEqual(self.query(r)['execution_status'],'rejected');self.assertEqual(self.calls,0)
    def test_changed_question_cannot_reuse_selected_evidence(self):
        self.assertEqual(self.query(self.record(),'Otra pregunta')['execution_status'],'rejected')
        self.assertEqual(self.calls,0)
    def test_no_evidence_does_not_establish_absence(self):
        r=self.query(self.record(empty=True));self.assertEqual(r['answer_status'],'no_retained_evidence')
        self.assertEqual(self.calls,0)
    def test_changed_source_rejected(self):
        r=self.record();self.path.write_text('Otra versión')
        self.assertEqual(self.query(r)['execution_status'],'rejected');self.assertEqual(self.calls,0)
    def test_hash_mismatch_rejected(self):
        r=query_traversal(self.a,self.sha,'Todas las fases',encode_record(self.record()),'bad',lambda *a:self.fail('called'))
        self.assertEqual(r['diagnostic'],'traversal_hash_or_size_mismatch')

if __name__=='__main__':unittest.main()
