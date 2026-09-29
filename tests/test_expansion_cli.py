import json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from agora import expansion_review as module
ROOT=Path(__file__).resolve().parents[1]
EX=ROOT/'examples/review-expansion'
class ExpansionCliTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.ws=self.root/'workspace';self.source=self.root/'source.txt';self.source.write_bytes((EX/'source.txt').read_bytes());self.plan=self.root/'plan.json'
  self.env=dict(os.environ,PYTHONPATH=str(ROOT/'src'),PYTHONDONTWRITEBYTECODE='1')
  for key in ('ZAI_API_KEY','SKOPOS_LLM_API_KEY','TYPESAFE_API_KEY'):self.env.pop(key,None)
 def cli(self,*args,code=0):
  p=subprocess.run([sys.executable,'-m','agora.issue_cli','--workspace',str(self.ws),*map(str,args)],env=self.env,capture_output=True,text=True,timeout=15)
  self.assertEqual(p.returncode,code,p.stdout+p.stderr);return json.loads(p.stdout)
 def prepare(self):
  self.cli('init');self.cli('review-init')
  original=self.cli('review-import','--review','original','--input',EX/'initial.json');self.parent=original['sha256']
  self.sourcehash=module.hashlib.sha256(self.source.read_bytes()).hexdigest()
  p=self.cli('expand-prepare','--parent','original','--expected-parent',self.parent,'--source',self.source,'--source-id','fixture','--source-sha256',self.sourcehash,'--out',self.plan)
  self.planhash=p['plan_sha256']
 def evaluate(self,provider='glm',identity='expanded',response=None,code=0):
  return self.cli('expand-evaluate','--review',identity,'--plan',self.plan,'--expected-plan-sha256',self.planhash,'--provider',provider,'--response',response or EX/(provider+'-response.json'),code=code)
 def test_replay_both_providers_preserves_parent_and_recovers_offline(self):
  self.prepare()
  self.cli('expand-inspect','--plan',self.plan,'--expected-plan-sha256',self.planhash,'--details')
  for provider in ('glm','jev'):
   result=self.evaluate(provider,provider)
   self.assertEqual(result['support'],'contradicted');self.assertEqual(result['origin'],'supplied_response_replay')
   self.assertEqual(result['parent']['sha256'],self.parent)
   self.assertEqual(result,self.evaluate(provider,provider))
   recovered=self.cli('review-recover','--operation',provider)
   self.assertFalse(recovered['provider_called']);self.assertEqual(result['sha256'],recovered['sha256'])
  parent=self.cli('review-inspect','--review','original');self.assertEqual(parent['sha256'],self.parent);self.assertEqual(parent['support'],'supported')
  self.source.unlink();self.cli('review-recover','--operation','glm')
 def test_changed_source_rejected_before_reservation(self):
  self.prepare();self.source.write_text('changed')
  self.evaluate(code=2)
  self.cli('review-inspect','--operation','expanded',code=2)
 def test_rehashed_altered_plan_rejected(self):
  self.prepare();p=module.read(self.plan);p['plan']['evidence']='Fabricated';p['sha256']=module.digest(p['plan']);self.planhash=p['sha256'];self.plan.write_text(json.dumps(p))
  result=self.evaluate(code=2);self.assertEqual(result['diagnostic'],'plan_reproduction_mismatch')
 def test_invalid_saved_response_stays_recoverable_not_overwritten(self):
  self.prepare();bad=self.root/'bad.json';bad.write_text('{"choices":[{"finish_reason":"length","message":{"content":"{}"}}]}')
  self.evaluate(response=bad,code=2)
  self.assertEqual(self.cli('review-inspect','--operation','expanded')['state'],'response_ready')
  self.cli('review-recover','--operation','expanded',code=2)
  self.assertEqual(self.evaluate(code=2)['diagnostic'],'review_operation_conflict')
 def test_missing_live_key_does_not_reserve(self):
  self.prepare()
  r=self.cli('expand-evaluate','--review','new','--plan',self.plan,'--expected-plan-sha256',self.planhash,'--provider','jev','--live',code=2)
  self.assertEqual(r['diagnostic'],'provider_key_missing');self.cli('review-inspect','--operation','new',code=2)
 def test_unknown_outcome_does_not_retry_provider(self):
  self.prepare();ledger=module.Ledger(self.ws/'reviews.sqlite3');self.addCleanup(ledger.close);calls=[]
  def lost(provider,plan):calls.append(provider);raise TimeoutError('lost')
  with self.assertRaises(TimeoutError):module.evaluate(ledger,'lost',module.read(self.plan),self.planhash,'glm',call=lost)
  with self.assertRaisesRegex(ValueError,'provider_outcome_unknown'):module.evaluate(ledger,'lost',module.read(self.plan),self.planhash,'glm',call=lost)
  self.assertEqual(calls,['glm']);self.assertEqual(ledger.get('operations','lost')['record']['state'],'attempted')
 def test_reinit_and_changed_import_are_rejected(self):
  self.prepare();self.cli('review-init',code=2)
  data=module.read(EX/'initial.json');data['claim']='Changed';p=self.root/'other.json';p.write_text(json.dumps(data))
  self.cli('review-import','--review','original','--input',p,code=2)
 def test_wrong_parent_and_plan_digest_rejected(self):
  self.prepare()
  self.cli('expand-prepare','--parent','original','--expected-parent','wrong','--source',self.source,'--source-id','fixture','--source-sha256',self.sourcehash,'--out',self.root/'other-plan.json',code=2)
  self.cli('expand-inspect','--plan',self.plan,'--expected-plan-sha256','wrong',code=2)
 def test_failed_commit_rolls_back_review_but_preserves_provider_response(self):
  self.prepare();ledger=module.Ledger(self.ws/'reviews.sqlite3');self.addCleanup(ledger.close)
  put=ledger.put;calls=[]
  def fail_after_insert(table,identity,body):
   result=put(table,identity,body)
   if table=='reviews':raise RuntimeError('simulated_crash')
   return result
  ledger.put=fail_after_insert
  def provider(name,plan):calls.append(name);return module.read(EX/'glm-response.json')
  with self.assertRaises(RuntimeError):module.evaluate(ledger,'atomic',module.read(self.plan),self.planhash,'glm',call=provider)
  self.assertIsNone(ledger.get('reviews','atomic'))
  self.assertEqual(ledger.get('operations','atomic')['record']['state'],'response_ready')
  ledger.put=put
  result=module.finalize(ledger,'atomic');self.assertEqual(result['record']['support'],'contradicted');self.assertEqual(calls,['glm'])
