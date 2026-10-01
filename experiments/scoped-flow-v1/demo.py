import json,hashlib,sys,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=load(B/'demo-freeze.json');d=B/'runs/demo';d.mkdir();cli=[str(R/'scripts/agora_issues.py'),'--workspace',str(B/'inputs/workspace')]
def call(args,key=None):
 cmd=[sys.executable]+cli+args
 if key:cmd=[sys.executable,str(R.parent/'llavero/llavero.py'),'ejecutar',key,'--']+cmd
 subprocess.run(cmd,check=True)
source=R/f['source'];rubric=R/f['rubric'];parent=R/f['candidate'];assert sha(source)==f['source_sha256'] and sha(rubric)==f['rubric_sha256'] and sha(parent)==f['candidate_sha256']
common=['--source',str(source),'--source-sha256',sha(source),'--rubric',str(rubric),'--rubric-sha256',sha(rubric),'--part-id','P1','--question',f['question']]
def review(candidate,folder,expand):
 folder.mkdir();ca=['--candidate',str(candidate),'--candidate-sha256',sha(candidate)]
 call(['review-rubric-scoped']+common+ca+['--live','--out',str(folder/'coverage')],'zai')
 call(['review-fidelity']+ca+['--live','--out',str(folder/'fidelity')],'agora.dev.typesafe')
 rv=folder/'coverage/result.json';fid=folder/'fidelity/result.json'
 call(['reading-route']+common+ca+['--review',str(rv),'--review-sha256',sha(rv),'--fidelity',str(fid),'--fidelity-sha256',sha(fid),'--out',str(folder/'route.json')]+(['--can-expand'] if expand else []))
 return rv,load(folder/'route.json')
rv,route=review(parent,d/'first',True)
if route['decision']!='expand':raise SystemExit('Second reading not authorized by route; retained')
plan=d/'proposal.json';ca=['--candidate',str(parent),'--candidate-sha256',sha(parent)];ra=['--review',str(rv),'--review-sha256',sha(rv)]
call(['coverage-plan']+common+ca+ra+['--query',f['question'],'--query-origin','Exact original question; fixed before execution','--budget','20000','--top-k','3','--following','3','--out',str(plan)])
if load(plan)['status']!='proposed':raise SystemExit('No new passages; retained')
call(['generate-recovery']+common+ca+ra+['--proposal',str(plan),'--proposal-sha256',sha(plan),'--response-language','en','--live','--out',str(d/'second-generation')],'zai')
review(d/'second-generation/result.json',d/'second',False)
