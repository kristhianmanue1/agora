"""Fresh bounded three-call diagnostic follow-up; never overwrites first campaign."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=Path(__file__).resolve().parent;root=b.parents[1];old=b/'runs/glm-01';out=b/'runs/format-02';out.mkdir(parents=True,exist_ok=False)
shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'));shutil.copyfile(b/'run.py',out/'worker.py');shutil.copyfile(__file__,out/'followup.py')
for name,path in [('C-language',old/'inputs/C-language.json'),('C-support',old/'inputs/C-support.json'),('N2-1024',old/'N2-1024/result.json')]:shutil.copyfile(path,out/(name+'.json'))
protocol={'max_calls':3,'change':'review prompt explicitly forbids Markdown/code fences and commentary outside JSON; no stripping/repair','model':'glm-5.3-flash','max_output_tokens':8192,'temperature':0,'socket_seconds':180,'process_seconds':200,'purpose':'known controls after fix; development evidence, not fresh holdout','expected':{'C-language':'mismatch','C-support':['supported','insufficient','contradicted'],'N2-1024':'flag claim2 A1-C1 unsupported by its own quotes; check irrelevant extras'},'limits':'same model; no independent adjudication; preserve first campaign'}
(out/'protocol.json').write_text(json.dumps(protocol,indent=2));freeze={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'freeze.json').write_text(json.dumps(freeze,indent=2))
rows=[];env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1')
for name in ('C-language','C-support','N2-1024'):
 assert all(sha(out/n)==h for n,h in freeze.items());dest=out/(name+'-review.json');start=time.monotonic()
 try:p=subprocess.run([sys.executable,str(out/'worker.py'),'--worker',str(out/(name+'.json')),str(dest)],env=env,timeout=200);code=p.returncode
 except subprocess.TimeoutExpired:code=None
 r=json.loads(dest.read_text()) if dest.exists() else {}
 row={'case':name,'status':r.get('execution_status','unknown'),'exit_code':code,'seconds':round(time.monotonic()-start,3),'tokens':r.get('response',{}).get('usage',{}).get('total_tokens'),'sha256':sha(dest) if dest.exists() else None};rows.append(row);(out/'execution.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
 if not r or r.get('execution_status')=='failed':raise SystemExit(2)
assert all(sha(out/n)==h for n,h in freeze.items())
