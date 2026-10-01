"""One bounded recovery via public CLI. Never retry an existing run."""
import hashlib,json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];P=R/'experiments/scoped-generalization-v1'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=load(B/'freeze.json')
assert sha(Path(__file__))==f['runner_sha256']
for name,digest in f['bindings'].items():assert sha(R/name)==digest,name
out=B/'runs';out.mkdir();cli=[sys.executable,str(R/'scripts/agora_issues.py'),'--workspace',str(P/'inputs/workspace-fixed')]
def call(args,key=None):
 cmd=cli+args
 if key:cmd=[sys.executable,str(R.parent/'llavero/llavero.py'),'ejecutar',key,'--']+cmd
 subprocess.run(cmd,check=True)
source=P/'inputs/case-2.txt';rubric=P/'case-2-rubric.json';parent=P/'runs-fixed/case-2/generation/result.json';rv=P/'runs-fixed/case-2/coverage/result.json';fid=P/'runs-fixed/case-2/fidelity/result.json'
common=['--source',str(source),'--source-sha256',sha(source),'--rubric',str(rubric),'--rubric-sha256',sha(rubric),'--part-id','P1','--question',f['question']]
ca=['--candidate',str(parent),'--candidate-sha256',sha(parent)];ra=['--review',str(rv),'--review-sha256',sha(rv)]
call(['reading-route']+common+ca+ra+['--fidelity',str(fid),'--fidelity-sha256',sha(fid),'--can-expand','--out',str(out/'first-route.json')])
assert load(out/'first-route.json')['decision']=='expand'
plan=out/'proposal.json'
call(['coverage-plan']+common+ca+ra+['--query',f['question'],'--query-origin','Exact original question, no reference answer terms added','--budget','20000','--top-k','4','--following','3','--out',str(plan)])
if load(plan)['status']!='proposed':raise SystemExit('No new passages; stop without provider')
call(['generate-recovery']+common+ca+ra+['--proposal',str(plan),'--proposal-sha256',sha(plan),'--response-language','es','--live','--out',str(out/'generation')],'zai')
candidate=out/'generation/result.json';ca=['--candidate',str(candidate),'--candidate-sha256',sha(candidate)]
call(['review-rubric-scoped']+common+ca+['--live','--out',str(out/'coverage')],'zai')
call(['review-fidelity']+ca+['--live','--out',str(out/'fidelity')],'agora.dev.typesafe')
rv=out/'coverage/result.json';fid=out/'fidelity/result.json'
call(['reading-route']+common+ca+['--review',str(rv),'--review-sha256',sha(rv),'--fidelity',str(fid),'--fidelity-sha256',sha(fid),'--out',str(out/'route.json')])
