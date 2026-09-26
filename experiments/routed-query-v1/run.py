"""Four explicit requests, no retry; real regression and two known new fixtures."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    base=Path(__file__).resolve().parent;root=base.parents[1];out=base/'runs/glm-01'
    out.mkdir(parents=True,exist_ok=False)
    shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
    for p in (base/'inputs').iterdir():shutil.copyfile(p,out/p.name)
    shutil.copyfile(__file__,out/'run.py')
    (out/'protocol.json').write_text(json.dumps({'max_calls':4,'model':'glm-5.3-flash','temperature':0,'max_output_tokens':8192,'socket_seconds':90,'process_deadline_seconds':110,'prompt_budget':65536,'holdout':False,'real_cases':'guided regression with four explicit parts, not original single-part request'},indent=2)+'\n')
    manifest={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
    (out/'freeze.json').write_text(json.dumps(manifest,indent=2)+'\n')
    env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1');rows=[]
    for c in json.loads((out/'cases.json').read_text()):
        cmd=[sys.executable,'-m','agora.routed_cli','--source',str(out/c['source']),'--source-id',c['source_id'],'--sha256',sha(out/c['source']),'--question',c['question'],'--parts',str(out/c['parts']),'--full-source-budget',str(c['full_source_budget']),'--model','glm-5.3-flash','--out',str(out/c['id'])]
        if c.get('traversal'):cmd+=['--traversal',str(out/c['traversal']),'--traversal-sha256',sha(out/c['traversal'])]
        start=time.monotonic()
        try:p=subprocess.run(cmd,env=env,timeout=110)
        except subprocess.TimeoutExpired:
            rows.append({'case':c['id'],'status':'deadline_exceeded','provider_outcome':'unknown'});(out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');return 2
        f=out/c['id']/'result.json';rows.append({'case':c['id'],'exit_code':p.returncode,'seconds':round(time.monotonic()-start,3),'result_sha256':sha(f) if f.exists() else None});(out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n')
        if not f.exists():return 2
        r=json.loads(f.read_text());print(json.dumps({'case':c['id'],'route':r.get('route'),'status':r.get('answer_status'),'tokens':r.get('response',{}).get('usage',{}).get('total_tokens')}),flush=True)
        if r['execution_status']=='failed':return 2
    assert all(sha(out/k)==v for k,v in manifest.items())
    return 0
if __name__=='__main__':raise SystemExit(main())
