"""One review call; same GLM transport and budgets for both review versions."""
from pathlib import Path
import json,os,subprocess,sys
from agora.evidence_review import review_evidence
source=Path(sys.argv[1]);out=Path(sys.argv[2]);version=sys.argv[3];transport=Path(sys.argv[4]);out.mkdir(parents=True,exist_ok=False)
attempts=0

def provider(system,user):
 global attempts
 if attempts:raise RuntimeError('request_budget_exceeded')
 payload={'model':'glm-5.3-flash','messages':[{'role':'system','content':system},{'role':'user','content':user}],'max_tokens':8192,'temperature':0,'response_format':{'type':'json_object'}}
 f=out/'request.json';f.write_text(json.dumps(payload));attempts+=1
 p=subprocess.run([sys.executable,str(transport),str(f),'180'],capture_output=True,text=True,timeout=180,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 receipt=json.loads(p.stdout)
 if p.returncode:raise RuntimeError(receipt.get('transport_error','transport_failed'))
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2));return receipt
r=review_evidence(json.loads(source.read_text()),provider,response_language='en',review_version=version)
r['http_attempts']=attempts;(out/'result.json').write_text(json.dumps(r,indent=2));print(json.dumps({'version':version,'status':r['execution_status'],'calls':attempts}),flush=True)
raise SystemExit(2 if r['execution_status']=='failed' else 0)
