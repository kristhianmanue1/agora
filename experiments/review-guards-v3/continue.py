"""Explicit continuation of unattempted cases only; never retry an unknown outcome."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time

b=Path(__file__).resolve().parent;root=b.parents[1];prior=b/'runs/glm-01';out=b/'runs/glm-01-continuation-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prior_hashes={str(p.relative_to(prior)):sha(p) for p in prior.rglob('*') if p.is_file()}
frozen=json.loads((prior/'freeze.json').read_text());assert all(sha(prior/n)==h for n,h in frozen.items())
for p in (prior/'code/agora').glob('*.py'):assert sha(p)==sha(root/'src/agora'/p.name)
rows=json.loads((prior/'execution.json').read_text());attempted={(x['case'],x['version']) for x in rows};assert len(rows)==6 and len(attempted)==6
cases=json.loads((prior/'inputs/pilot-01/cases.json').read_text());pending=[]
for i,c in enumerate(cases):
 for version in (['v2','v3'] if i%2==0 else ['v3','v2']):
  if (c['id'],version) not in attempted:pending.append((c,version))
assert len(pending)==10 and ('case-03','v3') in attempted
shutil.copytree(prior,out)
shutil.copyfile(out/'freeze.json',out/'base-freeze.json');shutil.copyfile(out/'execution.json',out/'base-execution.json')
shutil.copyfile(b/'continue.py',out/'continue.py');shutil.copyfile(b/'audit_continuation.py',out/'audit_continuation.py')
protocol={'base':'glm-01','base_files_sha256':prior_hashes,'max_new_calls':10,'max_new_reserved_output_tokens':81920,
 'pending':[{'case':c['id'],'version':v} for c,v in pending],'no_retries':True,'unknown_outcome_preserved':'v3/case-03',
 'model':'glm-5.3-flash','max_output_tokens':8192,'timeout_seconds':180,'worker_timeout_seconds':200,
 'response_format':{'type':'json_object'},'temperature':0,'stop':'transport/access/integrity failure or unknown usage',
 'metrics':'same frozen scores and gold; inherited timeout and missing cases remain in denominator'}
(out/'continuation-protocol.json').write_text(json.dumps(protocol,indent=2))
newfreeze={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and p.name not in ('freeze.json','execution.json')}
(out/'freeze.json').write_text(json.dumps(newfreeze,indent=2))
env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1')
for c,version in pending:
 assert all(sha(prior/n)==h for n,h in prior_hashes.items())
 assert all(sha(out/n)==h for n,h in newfreeze.items())
 dest=out/version/c['id'];assert not dest.exists();started=time.monotonic()
 try:
  p=subprocess.run([sys.executable,str(out/'worker.py'),str(out/'inputs/pilot-01'/c['candidate']),str(dest),version,str(out/'transport.py')],env=env,timeout=200);code=p.returncode
 except subprocess.TimeoutExpired:code=None
 f=dest/'result.json';r=json.loads(f.read_text()) if f.exists() else {};tokens=r.get('response',{}).get('usage',{}).get('total_tokens')
 row={'case':c['id'],'version':version,'status':r.get('execution_status','unknown'),'seconds':round(time.monotonic()-started,3),
      'exit_code':code,'tokens':tokens,'sha256':sha(f) if f.exists() else None,'diagnostics':r.get('diagnostics')}
 rows.append(row);(out/'execution.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
 if not r or r.get('execution_status')=='failed' or type(tokens) is not int or tokens<0:raise SystemExit(2)
assert all(sha(prior/n)==h for n,h in prior_hashes.items())
