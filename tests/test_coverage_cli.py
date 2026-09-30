import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from agora import coverage_cli as c

class CoverageTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.source=b'The model is SAT.';self.candidate=dict(schema='agora/claim-evidence-query/v2',execution_status='complete',source_sha256=c.digest(self.source),parts=[dict(id='P1',status='answered',claims=[dict(text='The model is SAT.',quotes=['The model is SAT.'],evidence_ids=['ev_local'])],missing=[])])
  self.raw=json.dumps(self.candidate).encode();(self.root/'source').write_bytes(self.source);(self.root/'candidate').write_bytes(self.raw);(self.root/'response').write_text(json.dumps(dict(content='{"coverage":"complete"}',finish_reason='stop')))
  self.args=SimpleNamespace(source=str(self.root/'source'),source_sha256=c.digest(self.source),candidate=str(self.root/'candidate'),candidate_sha256=c.digest(self.raw),part_id='P1',question='What model is used?',out=str(self.root/'out'),response=str(self.root/'response'),live=False)
 def tearDown(self):self.tmp.cleanup()
 def run_case(self):return c.run(self.args,lambda p:json.loads(Path(p).read_text()))
 def test_replay_no_network_no_admission(self):
  with patch.object(c,'live_provider',side_effect=AssertionError):r=self.run_case()
  self.assertEqual(r['coverage'],'complete');self.assertEqual(r['http_attempts'],0);self.assertEqual(r['disposition'],'requires_review');self.assertEqual((self.root/'candidate').read_bytes(),self.raw)
 def test_source_change_rejected_before_dispatch(self):
  (self.root/'source').write_text('Changed');self.args.live=True
  with patch.object(c,'live_provider',side_effect=AssertionError):self.assertEqual(self.run_case()['http_attempts'],0)
 def test_candidate_hash_mismatch(self):
  self.args.candidate_sha256='bad';self.assertEqual(self.run_case()['status'],'rejected')
 def test_nonliteral_quote_rejected(self):
  self.candidate['parts'][0]['claims'][0]['quotes']=['Other'];raw=json.dumps(self.candidate).encode()
  with self.assertRaises(ValueError):c.prepare(self.source,c.digest(self.source),raw,c.digest(raw),'P1','Question?')
 def test_bad_part(self):
  with self.assertRaises(ValueError):c.prepare(self.source,c.digest(self.source),self.raw,c.digest(self.raw),'P2','Question?')
 def test_strict_response(self):
  for content in ('{"coverage":"complete","coverage":"omitted"}','{"coverage":"approved"}','{"coverage":"complete","admit":true}'):
   with self.assertRaises(ValueError):c.assess(dict(finish_reason='stop',content=content))
 def test_truncated(self):
  with self.assertRaises(ValueError):c.assess(dict(finish_reason='length',content='{"coverage":"complete"}'))
 def test_timeout_preserved_no_retry(self):
  self.args.live=True
  with patch.object(c,'live_provider',side_effect=TimeoutError('private')) as p:r=self.run_case();self.assertEqual(p.call_count,1)
  self.assertEqual(r['status'],'failed');self.assertEqual(r['http_attempts'],1)
  self.assertNotIn('private',(self.root/'out/result.json').read_text())
  with self.assertRaises(FileExistsError):self.run_case()
 def test_reservation_before_call(self):
  self.args.live=True
  def provider(*a,**kw):
   self.assertEqual(json.loads((self.root/'out/result.json').read_text())['status'],'attempted');self.assertEqual(kw,dict(max_tokens=2048,json_object=True));return dict(content='{"coverage":"omitted"}',finish_reason='stop')
  with patch.object(c,'live_provider',side_effect=provider):self.assertEqual(self.run_case()['coverage'],'omitted')
 def test_exact_frozen_prompt(self):
  root=Path(__file__).resolve().parents[1];p=root/'experiments/reviewer-coverage-glm-v1/run.py';s=importlib.util.spec_from_file_location('frozen',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  state=dict(task='Q',answer={},full_source='S');_,payload=m.payload('glm',dict(axis='coverage',state=state));self.assertEqual(c.SYSTEM,payload['messages'][0]['content'])
if __name__=='__main__':unittest.main()
