import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from agora import rubric_cli as r
from agora.coverage_cli import digest

class RubricTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.source='SAT uses café data. It also has limitations.'.encode()
  self.candidate=json.dumps(dict(schema='agora/claim-evidence-query/v2',execution_status='complete',source_sha256=digest(self.source),parts=[dict(id='P1',status='answered',claims=[dict(text='SAT uses café data.',quotes=['SAT uses café data.'])],missing=[])])).encode()
  self.question='What does SAT use and what are its limitations?'
  self.rubric=dict(schema=r.RUBRIC,source_sha256=digest(self.source),question=self.question,provenance='Test producer; deliberately incomplete',requirements=[dict(id='R1',requirement='Name the data.',evidence=dict(text='SAT uses café data.',start_byte=0,end_byte=len('SAT uses café data.'.encode())))])
  (self.root/'source').write_bytes(self.source);(self.root/'candidate').write_bytes(self.candidate)
  self.args=SimpleNamespace(source=str(self.root/'source'),source_sha256=digest(self.source),candidate=str(self.root/'candidate'),candidate_sha256=digest(self.candidate),part_id='P1',question=self.question,rubric=str(self.root/'rubric'),out=str(self.root/'out'),live=False,response='unused')
  self.write_rubric();self.response=dict(finish_reason='stop',content='{"requirements":[{"id":"R1","status":"covered"}]}')
 def tearDown(self):self.tmp.cleanup()
 def write_rubric(self):
  self.raw=json.dumps(self.rubric).encode();Path(self.args.rubric).write_bytes(self.raw);self.args.rubric_sha256=digest(self.raw)
 def run_case(self):return r.run(self.args,lambda _:self.response)
 def test_incomplete_rubric_never_global_complete(self):
  with patch.object(r,'live_provider',side_effect=AssertionError):result=self.run_case()
  self.assertTrue(result['all_supplied_requirements_covered']);self.assertEqual(result['rubric_completeness'],'not_established');self.assertEqual(result['scope'],'supplied_requirements_only');self.assertEqual(result['http_attempts'],0);self.assertEqual(result['disposition'],'requires_review')
  saved=json.loads((self.root/'out/result.json').read_text());self.assertEqual(saved['provenance_status'],'caller_declared_not_verified');self.assertNotIn('coverage',saved);self.assertEqual((self.root/'candidate').read_bytes(),self.candidate)
 def test_binding_changes(self):
  for field in ('question','source_sha256','candidate_sha256','rubric_sha256'):
   with self.subTest(field=field):
    old=getattr(self.args,field);setattr(self.args,field,'changed')
    with self.assertRaises(ValueError):r.prepare(self.source,self.candidate,self.raw,self.args)
    setattr(self.args,field,old)
 def test_changed_rubric(self):
  with self.assertRaises(ValueError):r.prepare(self.source,self.candidate,self.raw+b' ',self.args)
 def test_bad_offsets(self):
  for end in (True,999,-1,15):
   self.rubric['requirements'][0]['evidence']['end_byte']=end;self.write_rubric()
   with self.assertRaises((ValueError,UnicodeDecodeError)):r.prepare(self.source,self.candidate,self.raw,self.args)
 def test_unknown_fields_and_duplicate_ids(self):
  self.rubric['requirements']*=2;self.write_rubric()
  with self.assertRaises(ValueError):r.prepare(self.source,self.candidate,self.raw,self.args)
 def test_response_set_is_exact(self):
  for items in ([],[dict(id='X',status='covered')],[dict(id='R1',status='covered')]*2,[dict(id='R1',status='approved')]):
   with self.assertRaises(ValueError):r.assess(dict(finish_reason='stop',content=json.dumps(dict(requirements=items))),['R1'])
 def test_response_duplicate_keys_and_truncation(self):
  with self.assertRaises(ValueError):r.assess(dict(finish_reason='stop',content='{"requirements":[],"requirements":[]}'),['R1'])
  with self.assertRaises(ValueError):r.assess(dict(self.response,finish_reason='length'),['R1'])
 def test_failure_once_and_no_reuse(self):
  self.args.live=True
  with patch.object(r,'live_provider',side_effect=TimeoutError('secret')) as provider:result=self.run_case()
  self.assertEqual(provider.call_count,1);self.assertEqual(result['status'],'failed');self.assertNotIn('secret',(self.root/'out/result.json').read_text())
  with self.assertRaises(FileExistsError):self.run_case()
 def test_bad_input_never_dispatches(self):
  self.args.live=True;self.args.question='changed'
  with patch.object(r,'live_provider') as provider:result=self.run_case()
  provider.assert_not_called();self.assertEqual(result['status'],'rejected')
 def test_live_reservation_and_budget(self):
  self.args.live=True
  def provider(*a,**kw):
   self.assertEqual(json.loads((self.root/'out/result.json').read_text())['status'],'attempted');self.assertEqual(kw,dict(max_tokens=2048,json_object=True));return self.response
  with patch.object(r,'live_provider',side_effect=provider):self.assertEqual(self.run_case()['status'],'complete')
if __name__=='__main__':unittest.main()
