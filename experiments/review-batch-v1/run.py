"""Frozen six-claim end-to-end queue pilot; no retry or repair."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/glm-01';out.mkdir(parents=True,exist_ok=False)
shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'));shutil.copyfile(__file__,out/'run.py');shutil.copyfile(b/'transport.py',out/'transport.py')
shutil.copyfile(root/'experiments/evidence-details-v2/runs/glm-01/inputs/R-regression.json',out/'candidate.json')
shutil.copyfile(root/'experiments/evidence-review-v1/runs/glm-01/inputs/N2.txt',out/'source.txt')
sys.path.insert(0,str(out/'code'));from agora.review_batch import ReviewBudget,review_candidate
budget=ReviewBudget()
protocol={'max_calls':6,'model':'glm-5.3-flash','temperature':0,'max_output_tokens_per_call':8192,'max_reserved_output_tokens':49152,'max_prompt_bytes_total':120000,'max_seconds':1200,'call_timeout_seconds':180,'retries':0,'provider_timeout':'HTTP timeout plus subprocess hard timeout using remaining batch time','expected':{'reviewed_jobs':6,'review_coverage':'complete','claim_2_support':'insufficient','claim_5_relevance':'extra'},'limits':'known development case; same model; no independent adjudication; byte/output caps not an exact all-token or monetary cap; no automatic admission'}
(out/'protocol.json').write_text(json.dumps(protocol,indent=2));frozen={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'freeze.json').write_text(json.dumps(frozen,indent=2))
rows=[];counter=0;checkpoint=0

def provider(system,user,*,max_output_tokens,timeout_seconds):
 global counter
 assert all(sha(out/n)==h for n,h in frozen.items())
 counter+=1;folder=out/'calls'/str(counter);folder.mkdir(parents=True,exist_ok=False)
 payload={'model':'glm-5.3-flash','messages':[{'role':'system','content':system},{'role':'user','content':user}],'max_tokens':max_output_tokens,'temperature':0}
 request=folder/'request.json';request.write_text(json.dumps(payload));start=time.monotonic();receipt=None;error=None
 try:
  p=subprocess.run([sys.executable,str(out/'transport.py'),str(request),str(timeout_seconds)],env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True,timeout=timeout_seconds)
  receipt=json.loads(p.stdout)
  if p.returncode:raise RuntimeError(receipt.get('transport_error','transport_failed'))
  (folder/'response.json').write_text(json.dumps(receipt,indent=2))
 except Exception as exc:error=type(exc).__name__
 row={'call':counter,'seconds':round(time.monotonic()-start,3),'timeout_seconds':timeout_seconds,'max_output_tokens':max_output_tokens,'tokens':receipt.get('usage',{}).get('total_tokens') if receipt else None,'error':error,'request_sha256':sha(request),'response_sha256':sha(folder/'response.json') if (folder/'response.json').exists() else None};rows.append(row);(out/'execution.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
 if error:raise RuntimeError(error)
 return receipt

def persist(result):
 global checkpoint
 checkpoint+=1;(out/f'checkpoint-{checkpoint:02}.json').write_text(json.dumps(result,indent=2))
 result_summary={'jobs_observed':len(result['jobs']),'reviewed':sum(j['status']=='reviewed' for j in result['jobs']),'status':result['execution_status'],'stop_reason':result['stop_reason']};print(json.dumps(result_summary),flush=True)

result=review_candidate(json.loads((out/'candidate.json').read_text()),provider,budget=budget,response_language='es',on_result=persist)
(out/'result.json').write_text(json.dumps(result,indent=2));assert all(sha(out/n)==h for n,h in frozen.items());print(json.dumps({k:result[k] for k in ('execution_status','review_coverage','expected_jobs','reviewed_jobs','recommendation','ledger','stop_reason')}),flush=True)
