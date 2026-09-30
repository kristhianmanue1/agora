import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from agora import omission_cli as o, coverage_cli as c

class OmissionTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.b=Path(self.t.name);self.source='Árbol.\n\nThe model is SAT.'.encode();self.candidate=json.dumps(dict(schema='agora/claim-evidence-query/v2',source_id='test',execution_status='complete',source_sha256=c.digest(self.source),parts=[dict(id='P1',status='not_in_passages',claims=[],missing=['Model name unavailable.'])])).encode();self.a=SimpleNamespace(source_sha256=c.digest(self.source),candidate_sha256=c.digest(self.candidate),part_id='P1',question='Which model?',live=False,out=str(self.b/'out'),source=str(self.b/'source'),candidate=str(self.b/'candidate'),review=str(self.b/'review'),response=str(self.b/'response'))
  self.review=dict(schema=c.VERSION,status='complete',coverage='omitted',**{k:getattr(self.a,k) for k in ('source_sha256','candidate_sha256','part_id','question')});self.raw=json.dumps(self.review).encode();self.a.review_sha256=c.digest(self.raw)
  for name,data in [('source',self.source),('candidate',self.candidate),('review',self.raw)]: (self.b/name).write_bytes(data)
  self.user,self.units,_=o.prepare(self.source,self.candidate,self.raw,self.a)
 def tearDown(self):self.t.cleanup()
 def response(self,status='proposed_omissions',ids=None):return dict(finish_reason='stop',content=json.dumps(dict(status=status,omissions=[dict(missing='The model is SAT.',evidence_ids=ids or [self.units[-1]['id']])] if status=='proposed_omissions' else [])))
 def test_exact_utf8_locator(self):
  _,f=o.validate(self.response(),self.units);e=f[0]['evidence'][0];self.assertEqual(self.source[e['start_byte']:e['end_byte']].decode(),e['text']);self.assertEqual(e['start_byte'],len('Árbol.\n\n'.encode()))
 def test_bad_ids(self):
  for ids in (['invented'],[self.units[0]['id']]*2):
   with self.assertRaises(ValueError):o.validate(self.response(ids=ids),self.units)
 def test_truncated(self):
  r=self.response();r['finish_reason']='length'
  with self.assertRaises(ValueError):o.validate(r,self.units)
 def test_mismatch_status(self):
  r=self.response();v=json.loads(r['content']);v['status']='no_omission_found';r['content']=json.dumps(v)
  with self.assertRaises(ValueError):o.validate(r,self.units)
 def test_review_binding(self):
  self.review['question']='Different';raw=json.dumps(self.review).encode();self.a.review_sha256=c.digest(raw)
  with self.assertRaises(ValueError):o.prepare(self.source,self.candidate,raw,self.a)
 def test_replay_preserves(self):
  (self.b/'response').write_text(json.dumps(self.response()));r=o.run(self.a,lambda p:json.loads(Path(p).read_text()));self.assertEqual(r['omission_count'],1);self.assertEqual(r['http_attempts'],0);self.assertEqual((self.b/'candidate').read_bytes(),self.candidate)
 def test_timeout_no_retry(self):
  self.a.live=True
  def fail(*a,**kw):
   self.assertEqual(json.loads((self.b/'out/result.json').read_text())['status'],'attempted');raise TimeoutError('secret')
  with patch.object(o,'live_provider',side_effect=fail) as p:r=o.run(self.a,None);self.assertEqual(p.call_count,1)
  self.assertEqual(r['status'],'failed');self.assertNotIn('secret',(self.b/'out/result.json').read_text())
  with self.assertRaises(FileExistsError):o.run(self.a,None)
 def test_truncated_replay_diagnostic(self):
  response=self.response();response['finish_reason']='length';(self.b/'response').write_text(json.dumps(response));r=o.run(self.a,lambda p:json.loads(Path(p).read_text()));self.assertEqual(r['diagnostic'],'generation_incomplete');self.assertIsNone(r['diagnosis_status'])
 def test_empty_diagnosis_preserves_disagreement(self):
  (self.b/'response').write_text(json.dumps(self.response(status='no_omission_found')));r=o.run(self.a,lambda p:json.loads(Path(p).read_text()));self.assertEqual(r['omission_count'],0);saved=json.loads((self.b/'out/result.json').read_text());self.assertTrue(saved['review_disagreement']);self.assertEqual(saved['disposition'],'requires_review')
 def test_explicit_budget(self):
  self.a.live=True;self.a.max_output_tokens=4096
  with patch.object(o,'live_provider',return_value=self.response()) as call:r=o.run(self.a,None)
  self.assertEqual(call.call_args.kwargs['max_tokens'],4096);self.assertEqual(json.loads((self.b/'out/result.json').read_text())['request_config']['max_tokens'],4096)
 def test_invalid_budget_before_reservation(self):
  self.a.max_output_tokens=4097
  with self.assertRaises(ValueError):o.run(self.a,None)
  self.assertFalse((self.b/'out').exists())
 def test_default_budget_preserved(self):
  self.a.live=True
  with patch.object(o,'live_provider',return_value=self.response()) as call:o.run(self.a,None)
  self.assertEqual(call.call_args.kwargs['max_tokens'],2048)
 def test_no_prior_label_in_prompt(self):
  self.assertEqual(set(json.loads(self.user)),{'task','answer','evidence_units'});self.assertNotIn('prior_coverage',self.user)
if __name__=='__main__':unittest.main()
