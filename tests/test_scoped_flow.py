import json,unittest
from pathlib import Path
from unittest.mock import patch
import test_coverage_recovery as fixtures
from agora import scoped_rubric as s,reading_route as route,fidelity_cli as fidelity,rubric_cli as legacy
from agora.coverage_cli import digest
class Tests(unittest.TestCase):
 tearDown=fixtures.RecoveryTests.tearDown
 set_review=fixtures.RecoveryTests.set_review
 save_review=fixtures.RecoveryTests.save_review
 def setUp(self):
  fixtures.RecoveryTests.setUp(self);self.args.can_expand=True;self.args.out=str(self.root/'route.json')
  for key,value in [('candidate',self.candidate),('rubric',self.raw)]:
   p=self.root/key;p.write_bytes(value);setattr(self.args,key,str(p))
  self.make('missing')
 def make(self,status,fid='supported'):
  self.set_review(status);self.review['schema']=s.VERSION;self.save_review();p=self.root/'review';p.write_bytes(self.review_bytes);self.args.review=str(p)
  request=fidelity.request(json.loads(self.candidate));response=dict(answers={k:dict(choice=fid) for k in request['questions']})
  self.fid=dict(schema=fidelity.VERSION,status='complete',candidate_sha256=self.args.candidate_sha256,request=request,response=response,label=fidelity.assess(response,request));self.save_fid()
 def save_fid(self):
  p=self.root/'fidelity';p.write_text(json.dumps(self.fid));self.args.fidelity=str(p);self.args.fidelity_sha256=digest(p.read_bytes())
 def run_route(self):return route.run(self.args,lambda p,v:None)
 def test_missing_expands_only_when_explicitly_available(self):
  self.assertEqual(self.run_route()['decision'],'expand');self.args.can_expand=False;self.assertEqual(self.run_route()['decision'],'insufficient_evidence')
 def test_distinguishes_missing_context_from_answer_omission(self):
  self.assertEqual(self.run_route()['gaps'][0]['kind'],'reference_not_in_read_context')
  candidate=json.loads(self.candidate);candidate['envelope']['spans']=[dict(start_byte=0,end_byte=len(self.source),text=self.source.decode())]
  self.candidate=json.dumps(candidate).encode();Path(self.args.candidate).write_bytes(self.candidate);self.args.candidate_sha256=digest(self.candidate);self.make('missing')
  self.assertEqual(self.run_route()['gaps'][0]['kind'],'answer_omission_of_supplied_reference')
 def test_covered_remains_candidate(self):
  self.make('covered');r=self.run_route();self.assertEqual(r['decision'],'candidate_ready_for_explicit_review');self.assertEqual(r['memory_admission'],'not_performed')
 def test_contradiction_not_remapped(self):
  self.make('contradicted');self.assertEqual(self.run_route()['decision'],'requires_coverage_inspection')
 def test_fidelity_blocks_even_if_covered(self):
  self.make('covered','insufficient');self.assertEqual(self.run_route()['decision'],'requires_fidelity_inspection')
 def test_binding_rejects_other_candidate(self):
  self.fid['candidate_sha256']='wrong';self.save_fid()
  with self.assertRaisesRegex(ValueError,'fidelity_binding'):self.run_route()
 def test_request_tampering_rejected(self):
  self.fid['request']['state']='changed';self.save_fid()
  with self.assertRaisesRegex(ValueError,'fidelity_request'):self.run_route()
 def test_scoped_input_exact_read_context(self):
  user,_=s.prepare(self.source,self.candidate,self.raw,self.args);self.assertEqual(json.loads(user)['read_context'],['Initial fact.'])
  c=json.loads(self.candidate);c['envelope']['spans'][0]['text']='changed';raw=json.dumps(c).encode();self.args.candidate_sha256=digest(raw)
  with self.assertRaisesRegex(ValueError,'invalid_read_context'):s.prepare(self.source,raw,self.raw,self.args)
 def test_legacy_contract_unchanged(self):
  self.assertEqual(legacy.VERSION,'agora/rubric-review/v1-experimental');self.assertNotIn('Scope rule:',legacy.SYSTEM)
 def test_new_review_can_prepare_recovery(self):
  from agora.coverage_recovery import build
  r=build(self.source,self.candidate,self.raw,self.review_bytes,self.args);self.assertEqual(r['status'],'proposed')
 def test_fidelity_exact_ids_and_no_reuse(self):
  body=fidelity.request(json.loads(self.candidate))
  with self.assertRaises(ValueError):fidelity.assess(dict(answers={}),body)
  self.args.live=False;self.args.response='unused';self.args.out=str(self.root/'fidelity-out')
  result=fidelity.run(self.args,lambda _:self.fid['response']);self.assertEqual(result['status'],'complete');self.assertEqual(result['http_attempts'],0)
  with self.assertRaises(FileExistsError):fidelity.run(self.args,lambda _:self.fid['response'])
if __name__=='__main__':unittest.main()
