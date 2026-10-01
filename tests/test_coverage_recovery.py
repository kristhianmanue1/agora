import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from agora import coverage_recovery as c, rubric_cli as r
from agora.coverage_cli import digest

class RecoveryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.source=b'Initial fact.\n\nMetrics list:\n\nAccuracy definition.\n\nDifference definition.'
  self.path=self.root/'source';self.path.write_bytes(self.source)
  self.candidate=json.dumps(dict(schema='agora/claim-evidence-query/v2',execution_status='complete',source_sha256=digest(self.source),source_id='test',envelope=dict(spans=[dict(start_byte=0,end_byte=13,text='Initial fact.')]),parts=[dict(id='P1',status='answered',claims=[dict(text='Initial fact.',quotes=['Initial fact.'])],missing=[])])).encode()
  self.raw=json.dumps(dict(schema=r.RUBRIC,source_sha256=digest(self.source),question='What metrics?',provenance='Synthetic test',requirements=[dict(id='R1',requirement='Deliberate oracle term NEVER_QUERY',evidence=dict(text='Difference definition.',start_byte=self.source.index(b'Difference'),end_byte=len(self.source)))])).encode()
  self.args=SimpleNamespace(source=str(self.path),source_sha256=digest(self.source),candidate_sha256=digest(self.candidate),rubric_sha256=digest(self.raw),part_id='P1',question='What metrics?',query=['metrics'],query_origin='Term from question',budget=100,top_k=1,following=3)
  self.set_review('missing')
 def tearDown(self):self.tmp.cleanup()
 def set_review(self,status):
  self.labels=[dict(id='R1',status=status)]
  self.review=dict(schema=r.VERSION,status='complete',requirements=self.labels,response=dict(finish_reason='stop',content=json.dumps(dict(requirements=self.labels))),**{k:getattr(self.args,k) for k in ('source_sha256','candidate_sha256','rubric_sha256','part_id','question')})
  self.save_review()
 def save_review(self):
  self.review_bytes=json.dumps(self.review).encode();self.args.review_sha256=digest(self.review_bytes)
 def build(self):return c.build(self.source,self.candidate,self.raw,self.review_bytes,self.args)
 def test_retrieval_preserves_context_and_recovers_tail_without_oracle(self):
  with patch.object(c,'prepare_subquestions',wraps=c.prepare_subquestions) as search:
   result=self.build()
  self.assertNotIn('NEVER_QUERY',json.dumps(search.call_args.args[2]));self.assertEqual(result['provider_calls'],0)
  self.assertGreater(result['new_bytes'],0);self.assertLessEqual(result['delivered_bytes'],100)
  spans=result['envelope']['spans'];text=' '.join(s['text'] for s in spans)
  self.assertIn('Initial fact.',text);self.assertIn('Difference definition.',text)
  self.assertEqual(result['stop_reason'],'explicit_execution_required');self.assertEqual(result['admission'],'not_performed')
 def test_uncertain_or_contradicted_stops_before_search(self):
  for status in ('uncertain','contradicted'):
   self.set_review(status)
   with patch.object(c,'prepare_subquestions') as search:result=self.build()
   search.assert_not_called();self.assertEqual(result['status'],'requires_review')
 def test_covered_is_not_global_completeness(self):
  self.set_review('covered')
  with patch.object(c,'prepare_subquestions') as search:result=self.build()
  search.assert_not_called();self.assertEqual(result['status'],'no_expansion');self.assertEqual(result['semantic_completeness'],'not_established')
 def test_budget_and_initial_context(self):
  self.args.budget=13;result=self.build()
  self.assertEqual(result['new_bytes'],0);self.assertEqual(result['ranges'],[[0,13]])
  self.args.budget=12
  with self.assertRaisesRegex(ValueError,'initial_context_exceeds_budget'):self.build()
 def test_review_binding_rejects_each_changed_field(self):
  for key in ('source_sha256','candidate_sha256','rubric_sha256','part_id','question'):
   original=self.review[key];self.review[key]='changed';self.save_review()
   with self.assertRaisesRegex(ValueError,'review_binding_mismatch'):self.build()
   self.review[key]=original
 def test_review_labels_must_match_response(self):
  self.review['requirements']=[dict(id='R1',status='covered')];self.save_review()
  with self.assertRaisesRegex(ValueError,'review_response_mismatch'):self.build()
 def test_review_hash_and_shape(self):
  self.review_bytes+=b' '
  with self.assertRaisesRegex(ValueError,'review_hash_mismatch'):self.build()
  self.review=[];self.save_review()
  with self.assertRaisesRegex(ValueError,'invalid_review'):self.build()
 def test_tampered_span_rejected_even_with_new_candidate_hash(self):
  candidate=json.loads(self.candidate);candidate['envelope']['spans'][0]['text']='False'
  self.candidate=json.dumps(candidate).encode();self.args.candidate_sha256=digest(self.candidate);self.set_review('missing')
  with self.assertRaisesRegex(ValueError,'invalid_initial_span'):self.build()
 def test_invalid_limits(self):
  for key,value in [('budget',True),('top_k',9),('following',4),('query','metrics'),('query',[]),('query_origin','')]:
   original=getattr(self.args,key);setattr(self.args,key,value)
   with self.assertRaises(ValueError):self.build()
   setattr(self.args,key,original)
 def test_changed_file_is_rejected_before_proposal(self):
  self.path.write_bytes(b'Changed source')
  with self.assertRaises(ValueError):self.build()
if __name__=='__main__':unittest.main()
