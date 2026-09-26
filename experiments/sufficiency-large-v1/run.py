"""Freeze and evaluate twelve predeclared synthetic operations, no retry or automatic actions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--execute',action='store_true')
    args=p.parse_args()
    if not args.execute or not os.environ.get('ZAI_API_KEY'):p.error('requires --execute and provider credential')
    base=Path(__file__).resolve().parent;root=base.parents[1];out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
    for f in base.iterdir():
        if f.is_file() and f.name!='.gitignore':shutil.copyfile(f,out/f.name)
    manifest={str(f.relative_to(out)):sha(f) for f in out.rglob('*') if f.is_file()}
    (out/'freeze.json').write_text(json.dumps(manifest,indent=2)+'\n')
    env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1');rows=[];failures=0
    for case in json.loads((out/'cases.json').read_text()):
        start=time.monotonic();dest=out/case['id']
        try:
            process=subprocess.run([sys.executable,str(out/'evaluate.py'),'--case',case['id'],'--out',str(dest)],env=env,capture_output=True,text=True,timeout=110)
        except subprocess.TimeoutExpired:
            rows.append({'case':case['id'],'execution_status':'deadline_exceeded','provider_outcome':'unknown'})
            (out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');return 2
        if not (dest/'result.json').exists():
            rows.append({'case':case['id'],'execution_status':'worker_failed','provider_outcome':'unknown','returncode':process.returncode})
            (out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');return 2
        r=json.loads((dest/'result.json').read_text())
        row={'case':case['id'],'seconds':round(time.monotonic()-start,3),'execution_status':r['execution_status'],
             'decision':r.get('judgment',{}).get('decision'),'http_attempts':r['http_attempts'],
             'usage':r.get('response',{}).get('usage'),'result_sha256':sha(dest/'result.json')}
        rows.append(row);(out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
        failures=failures+1 if r['execution_status']=='failed' else 0
        if failures>=2 or r.get('diagnostic')=='sensitive_response_rejected':return 2
    for name,h in manifest.items():
        if sha(out/name)!=h:raise RuntimeError('frozen_artifact_changed')
    return 0


if __name__=='__main__':raise SystemExit(main())
