"""Run frozen synthetic comparison, one request per route, no retry."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.execute:
        parser.error('explicit --execute required; sends synthetic source to GLM')
    if not os.environ.get('ZAI_API_KEY'):
        parser.error('provider key not available in environment')
    root = Path(__file__).resolve().parents[2]
    base = Path(__file__).resolve().parent
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    shutil.copytree(root / 'src/agora', out / 'code/agora', ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('N1.txt', 'N2.txt', 'N3.txt', 'N4.txt', 'N5.txt', 'cases.json', 'protocol.md', 'run.py'):
        shutil.copyfile(base / name, out / name)
    manifest = {str(p.relative_to(out)): digest(p) for p in out.rglob('*') if p.is_file()}
    (out / 'freeze.json').write_text(json.dumps(manifest, indent=2)+'\n')
    cases = json.loads((out / 'cases.json').read_text())
    env = dict(os.environ, PYTHONPATH=str(out / 'code'), PYTHONDONTWRITEBYTECODE='1')
    entries=[];failures=0
    for case in cases:
        revision = digest(out / case['source'])
        for mode in ('lexical', 'fallback'):
            dest=out / (case['id']+'-'+mode)
            command=[sys.executable,'-m','agora.passage_cli','--source',str(out/case['source']),
                '--source-id','synthetic-fallback-v1-'+case['id'],'--sha256',revision,'--question',case['question'],
                '--mode','retrieve','--content-budget','256',
                '--prompt-budget','65536','--max-output-tokens','2048','--timeout-seconds','90',
                '--model','glm-5.3-flash','--out',str(dest)]
            if mode=='fallback':command+=['--fallback-source-budget','8192']
            start=time.monotonic()
            try:
                process=subprocess.run(command,env=env,capture_output=True,text=True,timeout=110)
            except subprocess.TimeoutExpired:
                entries.append({'case':case['id'],'mode':mode,'execution_status':'deadline_exceeded',
                                'seconds':round(time.monotonic()-start,3),'provider_outcome':'unknown'})
                (out/'execution.json').write_text(json.dumps(entries,indent=2)+'\n')
                print('STOP: process deadline; provider outcome unknown; no retry',flush=True)
                return 2
            elapsed=time.monotonic()-start
            result=json.loads((dest/'result.json').read_text())
            entry={'case':case['id'],'mode':mode,'exit_code':process.returncode,'seconds':round(elapsed,3),
                   'execution_status':result['execution_status'],'answer_status':result.get('answer_status'),
                   'http_attempts':result['http_attempts'],'usage':result.get('response',{}).get('usage'),
                   'result_sha256':digest(dest/'result.json')}
            entries.append(entry)
            (out/'execution.json').write_text(json.dumps(entries,indent=2)+'\n')
            print(json.dumps(entry),flush=True)
            failures=failures+1 if result['execution_status']=='failed' else 0
            if failures>=2:
                print('STOP: consecutive provider/execution failures',flush=True);return 2
            if result.get('diagnostic')=='sensitive_response_rejected':return 2
    return 0


if __name__=='__main__':
    raise SystemExit(main())
