"""Execute only the independent, not-yet-attempted conflict after absence rejection."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from run import BASE, EXP, load, save, sha, checks

def main():
    os.umask(0o077)
    original=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve()
    prior=json.loads((original/'report.json').read_text())
    if prior.get('calls')!=1 or prior.get('detail')!='missing_evidence' or (original/'conflict').exists():
        raise ValueError('unexpected_prior_state')
    frozen=json.loads((original/'freeze.json').read_text())
    if any(sha(Path(p))!=v for p,v in frozen.items()):raise ValueError('original_freeze_changed')
    out.mkdir(parents=True,exist_ok=False)
    case=next(c for c in json.loads((original/'cases-and-gold.json').read_text()) if c['name']=='conflict')
    storage=load('conflict_store',EXP/'issue-store-v1/store.py')
    envelope=load('conflict_envelope',EXP/'skopos-issue-bridge-v2/envelope.py')
    request=dict(model='glm-5.3-flash',temperature=0,max_tokens=8192,response_format={'type':'json_object'},messages=[dict(role='system',content=storage.protocol.SYSTEM+'\n'+envelope.POLICY),dict(role='user',content=storage.encode(case['input']))])
    save(out/'request.json',request)
    save(out/'continuation.json',dict(original_report_sha256=sha(original/'report.json'),original_freeze_sha256=sha(original/'freeze.json'),continuation_code_sha256=sha(Path(__file__)),remaining_calls=1,retry_of_absence=False))
    report=dict(status='attempted',calls=1,known_tokens=0)
    save(out/'report.json',report)
    start=time.monotonic()
    try:
        proc=subprocess.run([sys.executable,str(EXP/'review-invariance-v1/transport_diagnostic.py'),str(out/'request.json'),'180'],capture_output=True,text=True,timeout=190)
        response=json.loads(proc.stdout);save(out/'response.json',response)
        usage=(response.get('usage') or {}).get('total_tokens')
        if type(usage) is int:report['known_tokens']=usage
        if proc.returncode or response.get('finish_reason')!='stop' or type(usage) is not int:raise ValueError('transport_or_usage_failed')
        assessment=storage.protocol.validate(response['content'],case['input'])
        navigation=[]
        for row in assessment['fields'].values():
            for ref in row['evidence']:
                hits=envelope.bridge.locate(case['packets'][ref['source_id']],ref['quote'])
                if not hits:raise ValueError('quote_not_in_selected_literal')
                navigation.append(dict(reference=ref,locators=hits))
        passed=checks(assessment,case['expected'],case['packets'])
        store=storage.Store(out/'issues.sqlite3',create=True)
        try:head=store.append('conflict',None,case['input'],response['content'],dict(kind='model_candidate',request=request,request_sha256=storage.digest(request),usage=response['usage'],admission='not_admitted'))
        finally:store.close()
        store=storage.Store(out/'issues.sqlite3')
        try:
            record=store.history('conflict',head)[-1]['record']
            assert [envelope.recover(s) for s in record['input']['sources']]==list(case['packets'].values())
        finally:store.close()
        report.update(status='complete',checks=passed,assessment=assessment,navigation=navigation,head=head,packets_recovered=True,usage=response['usage'],reported_model=response.get('reported_model'))
    except Exception as exc:
        report.update(status='failed',failure=type(exc).__name__,detail=str(exc)[:160] if isinstance(exc,ValueError) else 'execution_failed')
    finally:
        report['seconds']=round(time.monotonic()-start,3);save(out/'report.json',report);print(json.dumps(report,ensure_ascii=False))
    return 0 if report['status']=='complete' and all(report['checks'].values()) else 2
if __name__=='__main__':raise SystemExit(main())
