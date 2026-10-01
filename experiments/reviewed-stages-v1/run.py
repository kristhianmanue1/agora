import json,sys,hashlib,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.issue_cli import main
from policy import decide
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=load(B/'freeze.json')
for path,digest in f['implementations'].items():assert sha(R/path)==digest
(B/'runs').mkdir();(B/'inputs').mkdir();assert main(['--workspace',str(B/'inputs/workspace'),'init'])==0
for case in f['cases']:
 (B/'runs'/case['id']).mkdir()
 for index,stage in enumerate(case['stages']):
  out=B/'runs'/case['id']/str(index)
  def call(mode,key):subprocess.run([sys.executable,str(R.parent/'llavero/llavero.py'),'ejecutar',key,'--',sys.executable,str(B/'worker.py'),mode,case['id'],str(index)],check=True)
  call('glm','zai');candidate=load(out/'candidate.json');coverage=load(out/'review/result.json') if (out/'review/result.json').exists() else {};fidelity={}
  if candidate['execution_status']=='complete' and coverage.get('status')=='complete':call('jev','agora.dev.typesafe');fidelity=load(out/'fidelity/candidate.json')
  decision=decide(candidate['execution_status'],coverage,fidelity,index+1<len(case['stages']))
  with (out/'decision.json').open('x') as handle:json.dump(dict(decision=decision,candidate_sha256=sha(out/'candidate.json'),memory_admission='not_performed'),handle,indent=2)
  print(case['id'],stage['budget'],decision,flush=True)
  if decision!='expand':break
