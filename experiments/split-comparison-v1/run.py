"""Bounded paired comparison; synthetic inputs, no retries, frozen code."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    shutil.copytree(ROOT/'src/agora', out/'code/agora', ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(BASE/'run.py', out/'run.py')
    shutil.copyfile(BASE/'README.md', out/'protocol.md')
    shutil.copyfile(ROOT/'experiments/review-invariance-v1/transport_diagnostic.py', out/'transport.py')
    cases=[];gold={}
    for n,(quote,label) in enumerate([
        ('Maren carried a brass key.','supported'),
        ('The report does not specify what Maren carried.','insufficient'),
        ('Maren did not carry a brass key.','contradicted')]):
        for relevant in (True,False):
            identity=str(n+1)+('-on' if relevant else '-off')
            question='What did Maren carry?' if relevant else 'What was the weather?'
            candidate={'schema':'agora/claim-evidence-query/v2','execution_status':'complete','response_language':'en',
                       'prompt':{'user':json.dumps({'question':question})},
                       'requested_aspects':[{'id':'a','question':question}],
                       'parts':[{'id':'a','missing':[],'claims':[{'text':'Maren carried a brass key.','quotes':[quote]}]}]}
            cases.append({'id':identity,'candidate':candidate})
            gold[identity]={'support':label,'relevance':'relevant' if relevant else 'extra'}
    save(out/'cases.json',cases);save(out/'gold.json',gold)
    save(out/'budget.json',{'max_calls':18,'max_output_tokens_per_call':8192,
         'max_reserved_output_tokens':147456,'http_timeout':90,'process_timeout':100,
         'model':'glm-5.3-flash','retries':0,'stop':'transport failure or unknown usage',
         'baseline':'combined v1','candidate':'split v1','temperature':0})
    frozen={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
    save(out/'freeze.json',frozen)
    sys.path.insert(0,str(out/'code'))
    from agora.evidence_review import review_evidence
    from agora.split_review import review_split
    calls=[];rows=[];stop=False
    def provider(system,user):
        nonlocal stop
        if stop or len(calls)>=18:raise RuntimeError('budget_or_stop')
        if any(sha(out/p)!=h for p,h in frozen.items()):raise RuntimeError('frozen_input_changed')
        ordinal=len(calls)+1
        payload={'model':'glm-5.3-flash','messages':[{'role':'system','content':system},{'role':'user','content':user}],
                 'temperature':0,'max_tokens':8192,'response_format':{'type':'json_object'}}
        request=out/('request-%02d.json'%ordinal);save(request,payload)
        receipt={'ordinal':ordinal,'case':case['id'],'mode':mode,'status':'attempted','request_sha256':sha(request)}
        calls.append(receipt);save(out/'calls.json',calls)
        started=time.monotonic()
        try:
            run=subprocess.run([sys.executable,str(out/'transport.py'),str(request),'90'],
                               capture_output=True,text=True,timeout=100)
            response=json.loads(run.stdout)
            save(out/('response-%02d.json'%ordinal),response)
            receipt.update(seconds=round(time.monotonic()-started,3),response_sha256=sha(out/('response-%02d.json'%ordinal)))
            if run.returncode or 'transport_error' in response:
                receipt.update(status='failed',error=response.get('transport_error'),http_status=response.get('http_status'))
                raise RuntimeError('transport_failed')
            tokens=response.get('usage',{}).get('total_tokens')
            if type(tokens) is not int or tokens<0:raise RuntimeError('unknown_usage')
            receipt.update(status='complete',tokens=tokens,reported_model=response.get('reported_model'))
            return response
        except Exception as exc:
            stop=True;receipt.update(status='failed',seconds=round(time.monotonic()-started,3),failure_type=type(exc).__name__)
            raise
        finally:
            save(out/'calls.json',calls)
            print(json.dumps(receipt),flush=True)
    for index,case in enumerate(cases):
        # Alternate arm order; split's support precedes relevance by contract.
        for mode in (('combined','split') if index%2==0 else ('split','combined')):
            started=time.monotonic()
            result=review_evidence(case['candidate'],provider) if mode=='combined' else review_split(case['candidate'],provider,provider)
            dest=out/(case['id']+'-'+mode+'.json');save(dest,result)
            complete=result['execution_status']=='complete'
            assessment=result.get('assessment',{})
            claim=(assessment['claims'][0] if mode=='combined' else assessment[0]) if complete else {}
            expected=gold[case['id']]
            rows.append({'case':case['id'],'mode':mode,'status':result['execution_status'],
                         'seconds':round(time.monotonic()-started,3),'result_sha256':sha(dest),
                         'support_correct':complete and claim.get('support')==expected['support'],
                         'relevance_correct':complete and claim.get('relevance')==expected['relevance'],
                         'joint_correct':complete and all(claim.get(k)==v for k,v in expected.items())})
            save(out/'scores.json',rows)
            if stop:break
        if stop:break
    summary={'planned_cases':6,'planned_arms':12,'attempted_arms':len(rows),'attempted_calls':len(calls),
             'known_tokens':sum(c.get('tokens',0) for c in calls),'unknown_usage_calls':sum('tokens' not in c for c in calls),
             'stopped':stop,'arms':{m:{'attempted':sum(r['mode']==m for r in rows),
                  'complete':sum(r['mode']==m and r['status']=='complete' for r in rows),
                  'joint_correct':sum(r['mode']==m and r['joint_correct'] for r in rows)} for m in ('combined','split')},
             'frozen_files_verified':all(sha(out/p)==h for p,h in frozen.items())}
    save(out/'summary.json',summary);print(json.dumps(summary),flush=True)
    return 2 if stop else 0

if __name__=='__main__':raise SystemExit(main())
