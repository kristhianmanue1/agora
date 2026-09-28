"""Comparación acotada, conservación de intentos y evaluación posterior."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]

def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    os.umask(0o077)
    out=Path(sys.argv[1]).resolve()
    out.mkdir(parents=True,exist_ok=False)
    for name in ('cases.json','gold.json','protocol.py','run.py','README.md','build_cases.py'):
        shutil.copyfile(BASE/name,out/name)
    shutil.copyfile(ROOT/'experiments/review-invariance-v1/transport_diagnostic.py',out/'transport.py')
    frozen={p.name:sha(p) for p in out.iterdir() if p.is_file()}
    save(out/'freeze.json',frozen)
    sys.path.insert(0,str(out))
    from protocol import SYSTEM,payload,validate,score
    cases=json.loads((out/'cases.json').read_text());gold=json.loads((out/'gold.json').read_text())
    save(out/'budget.json',dict(max_calls=24,max_output_tokens=8192,http_timeout=90,process_timeout=100,retries=0,model='glm-5.3-flash'))
    calls=[]; rows=[]; stopped=False
    for index,case in enumerate(cases):
        previous=None
        for stage in (0,1):
            for mode in (('full','tracked') if index%2==0 else ('tracked','full')):
                ordinal=len(calls)+1
                row=dict(case=case['id'],stage=stage,mode=mode,status='attempted')
                calls.append(row)
                started=time.monotonic()
                try:
                    if ordinal>24 or any(sha(out/p)!=h for p,h in frozen.items()): raise ValueError('budget_or_freeze')
                    data=payload(case,stage,previous if mode=='tracked' else None)
                    request=dict(model='glm-5.3-flash',temperature=0,max_tokens=8192,response_format={'type':'json_object'},messages=[dict(role='system',content=SYSTEM),dict(role='user',content=json.dumps(data,ensure_ascii=False))])
                    req=out/f'request-{ordinal:02}.json';save(req,request)
                    row['request_sha256']=sha(req);save(out/'calls.json',calls)
                    proc=subprocess.run([sys.executable,str(out/'transport.py'),str(req),'90'],capture_output=True,text=True,timeout=100)
                    response=json.loads(proc.stdout)
                    dest=out/f'response-{ordinal:02}.json';save(dest,response)
                    row['response_sha256']=sha(dest)
                    usage=response.get('usage') or {};tokens=usage.get('total_tokens')
                    if type(tokens) is int and tokens>=0:row['tokens']=tokens
                    row['reported_model']=response.get('reported_model')
                    if proc.returncode or 'transport_error' in response:
                        row['http_status']=response.get('http_status');raise ValueError('transport_failure')
                    if 'tokens' not in row:raise ValueError('unknown_usage')
                    if response.get('finish_reason')!='stop':raise ValueError('incomplete_generation')
                    result=validate(response['content'],data)
                    save(out/f'assessment-{ordinal:02}.json',result)
                    if mode=='tracked':previous=result
                    checks=score(result,gold[case['id']][stage])
                    rows.append(dict(case=case['id'],stage=stage,mode=mode,checks=checks,joint_correct=all(checks.values()),false_closure=result['status']=='resolved' and gold[case['id']][stage]['status']!='resolved'))
                    row['status']='complete'
                except Exception as exc:
                    row.update(status='failed',failure_type=type(exc).__name__,failure=str(exc)[:120] if isinstance(exc,ValueError) else 'execution_failed')
                    stopped=True
                finally:
                    row['seconds']=round(time.monotonic()-started,3)
                    save(out/'calls.json',calls);save(out/'scores.json',rows)
                    print(json.dumps(row),flush=True)
                if stopped:break
            if stopped:break
        if stopped:break
    summary=dict(planned_calls=24,attempted_calls=len(calls),completed=len(rows),stopped=stopped,
                 known_tokens=sum(c.get('tokens',0) for c in calls),unknown_usage_calls=sum('tokens' not in c for c in calls),
                 frozen_files_verified=all(sha(out/p)==h for p,h in frozen.items()),
                 arms={mode:dict(completed=sum(r['mode']==mode for r in rows),joint_correct=sum(r['mode']==mode and r['joint_correct'] for r in rows),false_closures=sum(r['mode']==mode and r['false_closure'] for r in rows),tokens=sum(c.get('tokens',0) for c in calls if c['mode']==mode),seconds=round(sum(c['seconds'] for c in calls if c['mode']==mode),3)) for mode in ('full','tracked')})
    save(out/'summary.json',summary);print(json.dumps(summary),flush=True)
    return 2 if stopped or not summary['frozen_files_verified'] else 0
if __name__=='__main__':raise SystemExit(main())
