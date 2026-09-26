"""Freeze six stages, maximum twelve requests, no retry."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    base=Path(__file__).resolve().parent;root=base.parents[1]
    out=base/'runs/glm-02';out.mkdir(parents=True,exist_ok=False)
    shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('source.txt','cases.json','provenance.json'):shutil.copyfile(base/'inputs'/name,out/name)
    for name in ('worker.py','run.py'):shutil.copyfile(base/name,out/name)
    (out/'protocol.json').write_text(json.dumps({'max_requests':12,'model':'glm-5.3-flash','max_tokens':8192,'temperature':0,'socket_seconds':90,'walk_calls':4,'walk_unit_bytes':4096,'known_cases':True,'full_source_baseline':True,'purpose':'documentary fidelity only; not medical or financial validation'},indent=2)+'\n')
    manifest={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
    (out/'freeze.json').write_text(json.dumps(manifest,indent=2)+'\n')
    env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1');rows=[]
    for case in json.loads((out/'cases.json').read_text()):
        for stage in ('baseline','walk','answer'):
            try:completed=subprocess.run([sys.executable,str(out/'worker.py'),'--case',case['id'],'--stage',stage],env=env,timeout=400 if stage=='walk' else 110)
            except subprocess.TimeoutExpired:
                rows.append({'case':case['id'],'stage':stage,'status':'deadline_exceeded','provider_outcome':'unknown'})
                (out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');return 2
            f=out/case['id']/stage/'result.json'
            rows.append({'case':case['id'],'stage':stage,'exit_code':completed.returncode,'result_sha256':sha(f) if f.exists() else None})
            (out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n')
            if completed.returncode:return 2
    assert all(sha(out/k)==v for k,v in manifest.items())
    return 0
if __name__=='__main__':raise SystemExit(main())
