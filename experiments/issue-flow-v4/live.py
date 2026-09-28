"""One real request through v4; new-process recovery without provider invocation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import recovery
from fixtures import seed
BASE=Path(__file__).resolve().parent

def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def forbidden(request):raise AssertionError('unexpected_provider_call')

def main():
    if sys.argv[1]=='recover':
        out=Path(sys.argv[2]);store=recovery.Store(out/'issues.sqlite3')
        try:
            prepared=json.loads((out/'prepared.json').read_text())
            result=recovery.evaluate(store,'live-v4-001',prepared,forbidden)
            history=store.history('nube',result['revision_sha256'])
            print(recovery.encode(dict(result=result,history=history,operation=recovery.inspect(store,'live-v4-001'))))
        finally:store.close()
        return 0
    os.umask(0o077);out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
    store=recovery.Store(out/'issues.sqlite3',create=True)
    head,source=seed(store);initial=store.history('nube',head)[0]
    prepared=recovery.flow.prepare(store,'nube',head,source,'2026-10-09')
    save(out/'prepared.json',prepared)
    save(out/'budget-and-expectations.json',dict(max_calls=1,max_output_tokens=8192,http_timeout=180,process_timeout=190,retries=0,expected_status='resolved',expected_values={'date':'2026-10-21','owner':'Lina'},scope_sources=2,semantic_review='Literal support, no global completeness claim, no independent corroboration inferred.'))
    paths=[BASE/n for n in ('store.py','adapter.py','recovery.py','fixtures.py','live.py')]+[BASE.parent/'open-issues-v4/protocol.py',BASE.parent/'skopos-issue-bridge-v2/envelope.py',BASE.parent/'skopos-issue-bridge-v1/bridge.py',BASE.parent/'review-invariance-v1/transport_diagnostic.py',out/'prepared.json',out/'budget-and-expectations.json']
    frozen={str(p):sha(p) for p in paths};save(out/'freeze.json',frozen)
    report=dict(status='prepared',real_model_calls=0,known_tokens=0)
    def provider(request):
        if any(sha(Path(p))!=v for p,v in frozen.items()):raise ValueError('freeze_changed')
        save(out/'request.json',request)
        report.update(status='attempted',real_model_calls=1);save(out/'report.json',report)
        start=time.monotonic()
        try:
            proc=subprocess.run([sys.executable,str(BASE.parent/'review-invariance-v1/transport_diagnostic.py'),str(out/'request.json'),'180'],capture_output=True,text=True,timeout=190)
            response=json.loads(proc.stdout);save(out/'response.json',response)
            report['usage']=response.get('usage');report['reported_model']=response.get('reported_model')
            tokens=(response.get('usage') or {}).get('total_tokens')
            if type(tokens) is int:report['known_tokens']=tokens
            if proc.returncode:raise ValueError('transport_failed')
            return response
        finally:
            report['seconds']=round(time.monotonic()-start,3);save(out/'report.json',report)
    try:
        result=recovery.evaluate(store,'live-v4-001',prepared,provider)
        save(out/'candidate.json',result);store.close();store=None
        proc=subprocess.run([sys.executable,str(BASE/'live.py'),'recover',str(out)],capture_output=True,text=True,check=True,timeout=15)
        restored=json.loads(proc.stdout);save(out/'recovered.json',restored)
        if restored['result']!=result or len(restored['history'])!=2 or restored['history'][0]!=initial:raise ValueError('recovery_mismatch')
        if restored['operation']['request']['provider']!=json.loads((out/'request.json').read_text()):raise ValueError('request_mismatch')
        assessment=result['assessment']
        checks=dict(status=assessment['status']=='resolved',values={k:v['observed_value'] for k,v in assessment['fields'].items()}=={'date':'2026-10-21','owner':'Lina'},scope_sources=len(assessment['reviewed_scope']['sources'])==2,original_revision_preserved=True,new_process_recovery=True,request_exactly_persisted=True)
        report.update(status='complete',checks=checks,result=result,operation_state=restored['operation']['state'],semantic_review='pending producer review')
    except Exception as exc:
        report.update(status='failed',failure=type(exc).__name__,detail=str(exc)[:160] if isinstance(exc,ValueError) else 'execution_failed',retry='none')
    finally:
        if store is not None:
            op=recovery.inspect(store,'live-v4-001');report['operation_state']=op['state'] if op else 'none';store.close()
        report['frozen_files_verified']=all(sha(Path(p))==v for p,v in frozen.items());save(out/'report.json',report);print(json.dumps(report,ensure_ascii=False))
    return 0 if report['status']=='complete' and all(report['checks'].values()) and report['frozen_files_verified'] else 2
if __name__=='__main__':raise SystemExit(main())
