import json
from pathlib import Path
from unittest.mock import Mock,patch
import unittest
import test_coverage_recovery as fixtures
from agora import recovery_generation as g, coverage_recovery as c
from agora.coverage_cli import digest

class GenerationTests(unittest.TestCase):
 tearDown=fixtures.RecoveryTests.tearDown
 build=fixtures.RecoveryTests.build
 set_review=fixtures.RecoveryTests.set_review
 save_review=fixtures.RecoveryTests.save_review
 def setUp(self):
  fixtures.RecoveryTests.setUp(self)
  for key,raw in [('candidate',self.candidate),('rubric',self.raw),('review',self.review_bytes)]:
   path=self.root/key;path.write_bytes(raw);setattr(self.args,key,str(path))
  self.args.proposal=str(self.root/'proposal');self.args.response_language='en';self.args.live=False;self.args.response=str(self.root/'response');self.args.out=str(self.root/'output')
  plan=self.build();plan['implementation_sha256']=digest(Path(c.__file__).read_bytes());self.write_plan(plan)
 def write_plan(self,plan):
  raw=json.dumps(plan).encode();Path(self.args.proposal).write_bytes(raw);self.args.proposal_sha256=digest(raw)
 def provider(self,system,user):
  data=json.loads(user);unit=data['evidence_units'][0]
  return dict(finish_reason='stop',content=json.dumps(dict(parts=[dict(id='P1',status='answered',claims=[dict(text=unit['text'],evidence_ids=[unit['id']])],missing=[])])))
 def test_generates_with_lineage_and_only_planned_evidence(self):
  calls=[]
  def provider(system,user):calls.append(json.loads(user));return self.provider(system,user)
  result=g.generate(self.args,provider)
  self.assertEqual(result['execution_status'],'complete');self.assertEqual(len(calls),1)
  self.assertEqual(result['parent_candidate_sha256'],digest(self.candidate));self.assertEqual(result['memory_admission'],'not_performed')
  self.assertNotIn('NEVER_QUERY',json.dumps(calls));self.assertEqual(result['semantic_support'],'not_verified')
  plan=json.loads(Path(self.args.proposal).read_bytes())
  self.assertEqual(result['envelope'],plan['envelope'])
 def test_tampered_proposal_rejected_with_recomputed_hash(self):
  for field,value in [('ranges',[[0,1]]),('new_bytes',999),('status','no_expansion'),('implementation_sha256','changed')]:
   plan=json.loads(Path(self.args.proposal).read_bytes());original=dict(plan);plan[field]=value;self.write_plan(plan);provider=Mock()
   with self.assertRaises(ValueError):g.generate(self.args,provider)
   provider.assert_not_called();self.write_plan(original)
 def test_changed_bound_input_rejected_before_dispatch(self):
  Path(self.args.review).write_bytes(self.review_bytes+b' ');provider=Mock()
  with self.assertRaises(ValueError):g.generate(self.args,provider)
  provider.assert_not_called()
 def test_live_failure_one_call_and_reserved_directory(self):
  self.args.live=True
  with patch.object(g,'live_provider',side_effect=TimeoutError) as provider:
   result=g.run(self.args,lambda p:json.loads(Path(p).read_text()))
  self.assertEqual(provider.call_count,1);self.assertEqual(result['http_attempts'],1);self.assertEqual(result['status'],'failed')
  with self.assertRaises(FileExistsError):g.run(self.args,lambda _:None)
 def test_live_settings_and_attempt_receipt(self):
  self.args.live=True
  def provider(system,user,**kwargs):
   self.assertEqual(kwargs,dict(max_tokens=4096,json_object=True));self.assertEqual(json.loads((Path(self.args.out)/'result.json').read_text())['execution_status'],'attempted')
   return self.provider(system,user)
  with patch.object(g,'live_provider',side_effect=provider):result=g.run(self.args,lambda _:None)
  self.assertEqual(result['status'],'complete');self.assertTrue((Path(self.args.out)/'response.json').exists())
