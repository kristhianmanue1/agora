"""Four bounded v2 review calls; strict JSON, no repair or retry."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/glm-01';out.mkdir(parents=True,exist_ok=False)
shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(b/'inputs',out/'inputs');shutil.copyfile(__file__,out/'run.py')
worker=(root/'experiments/evidence-review-v1/run.py').read_text();old="provider,response_language='es')";assert old in worker
worker=worker.replace(old,"provider,response_language='es',review_version='v2')")
(out/'worker.py').write_text(worker)
protocol={'max_calls':4,'model':'glm-5.3-flash','temperature':0,'max_output_tokens':8192,'socket_seconds':180,'process_seconds':200,'retries':0,'review_version':'v2','expected_labels':'inputs/cases.json; withheld from provider','control_method':'known real regression and new synthetic positive/negative paired claims','limitations':'producer authored fixtures; same model; no independent adjudication; v2 literal text coverage is not proof of semantic decomposition','stop':'transport/access/integrity failure; structural rejects preserved'}
(out/'protocol.json').write_text(json.dumps(protocol,indent=2));frozen={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'freeze.json').write_text(json.dumps(frozen,indent=2))
rows=[];env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1')
for case in json.loads((out/'inputs/cases.json').read_text()):
 assert all(sha(out/n)==h for n,h in frozen.items());cid=case['id'];dest=out/(cid+'-review.json');start=time.monotonic()
 try:p=subprocess.run([sys.executable,str(out/'worker.py'),'--worker',str(out/'inputs'/(cid+'.json')),str(dest)],env=env,timeout=200);code=p.returncode
 except subprocess.TimeoutExpired:code=None
 r=json.loads(dest.read_text()) if dest.exists() else {}
 row={'case':cid,'status':r.get('execution_status','unknown'),'exit_code':code,'seconds':round(time.monotonic()-start,3),'tokens':r.get('response',{}).get('usage',{}).get('total_tokens'),'sha256':sha(dest) if dest.exists() else None,'diagnostics':r.get('diagnostics')};rows.append(row)
 (out/'execution.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
 if not r or r.get('execution_status')=='failed':raise SystemExit(2)
assert all(sha(out/n)==h for n,h in frozen.items())
