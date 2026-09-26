"""At most 24 calls, no retries; freeze inputs, code, scoring and protocol first."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, time

b = Path(__file__).resolve().parent
root = b.parents[1]
out = b / 'runs/glm-01'
out.mkdir(parents=True, exist_ok=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copytree(root/'src/agora', out/'code/agora', ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(b/'inputs', out/'inputs')
for name in ('worker.py','run.py','prepare.py','score.py','audit.py'):
    shutil.copyfile(b/name, out/name)
shutil.copyfile(root/'experiments/review-batch-v1/transport.py', out/'transport.py')
shutil.copyfile(root/'docs/controles-revision-01.md', out/'protocol.md')
protocol = {'max_calls':24,'model':'glm-5.3-flash','temperature':0,'max_output_tokens':8192,
    'max_reserved_output_tokens':196608,'http_and_transport_timeout_seconds':180,'worker_timeout_seconds':200,
    'retries':0,'versions':['v1','v2'],'language':'en','order':'alternate versions by hashed case order',
    'stop':'transport/access/integrity failure or unknown total usage; retain structural rejections',
    'metrics':'all-axis and per-axis exact match; positive/negative and whole-pair success; failed/missing retained; usage and time',
    'limits':'authored diagnostic controls; no authentication of external authors, no Spanish/long-document/generalization claims'}
(out/'protocol.json').write_text(json.dumps(protocol,indent=2))
frozen = {str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'freeze.json').write_text(json.dumps(frozen,indent=2))
rows=[]
env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1')
cases=json.loads((out/'inputs/pilot-01/cases.json').read_text())
assert len(cases)==12
for i,c in enumerate(cases):
    for version in (['v1','v2'] if i%2==0 else ['v2','v1']):
        assert all(sha(out/n)==h for n,h in frozen.items())
        dest=out/version/c['id'];start=time.monotonic()
        try:
            p=subprocess.run([sys.executable,str(out/'worker.py'),str(out/'inputs/pilot-01'/c['candidate']),str(dest),version,str(out/'transport.py')],env=env,timeout=200)
            code=p.returncode
        except subprocess.TimeoutExpired: code=None
        f=dest/'result.json';r=json.loads(f.read_text()) if f.exists() else {}
        tokens=r.get('response',{}).get('usage',{}).get('total_tokens')
        row={'case':c['id'],'version':version,'status':r.get('execution_status','unknown'),
             'seconds':round(time.monotonic()-start,3),'exit_code':code,'tokens':tokens,
             'sha256':sha(f) if f.exists() else None,'diagnostics':r.get('diagnostics')}
        rows.append(row);(out/'execution.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
        if not r or r.get('execution_status')=='failed' or type(tokens) is not int or tokens<0: raise SystemExit(2)
assert all(sha(out/n)==h for n,h in frozen.items())
