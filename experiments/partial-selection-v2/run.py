"""Cold evaluations: missing evidence versus explicit contradictory evidence."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
BASE = Path(__file__).resolve().parent
EXP = BASE.parent
ROOT = EXP.parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def checks(assessment, expected, packets):
    fields = assessment['fields']
    cited = {ref['source_id'] for ref in fields['date']['evidence']}
    return dict(status=assessment['status']=='partial',
                values={k:v['observed_value'] for k,v in fields.items()}=={'date':None,'owner':'Lina'},
                support=fields['date']['support_status']==expected,
                both_conflicting_sources=expected!='disputed' or set(packets)<=cited)

def main():
    os.umask(0o077)
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    envelope = load('cold_envelope', EXP/'skopos-issue-bridge-v2/envelope.py')
    storage = load('cold_storage', EXP/'issue-store-v1/store.py')
    skopos = ROOT.parent/'skopos/experiments/meeting-source-v1'
    pilot = load('cold_pilot', skopos/'pilot.py')
    export = load('cold_export', skopos/'export.py')
    cases=[]
    for name, texts, expected in [
        ('absence', [('Lina es responsable de Nube.', 'Calendario: Nube se entrega el 2026-10-21.')], 'missing'),
        ('conflict', [('Acuerdo del 2026-10-08: Nube se entrega el 2026-10-21. Lina es responsable.',), ('Acuerdo del 2026-10-08: Nube se entrega el 2026-10-28. Lina es responsable.',)], 'disputed')]:
        sources=[]; packets={}
        for index, segments in enumerate(texts):
            original=dict(source_id=name+'-'+str(index),revision=1,supersedes=None,complete=False,segments=[dict(id='s'+str(n),start_ms=n*10000,end_ms=n*10000+9000,speaker='Coordinación sintética',text=text) for n,text in enumerate(segments)])
            path=out/(name+'-'+str(index)+'.json');save(path,original)
            producer=pilot.MeetingStore();producer.ingest(path)
            packet=export.export_packet(producer,['Lina'])
            source,_=envelope.create(packet,'2026-10-08',producer.fetch)
            sources.append(source);packets[source['id']]=packet
        data=dict(question='¿Fecha y responsable de entrega de Nube?',as_of='2026-10-08',requirements=dict(date=['date_confirmed'],owner=['owner_confirmed']),sources=sources,dependents=[],previous_assessment=None)
        if name=='absence':
            assert '2026-10-21' not in json.dumps(data) and 'pendiente' not in json.dumps(data)
        cases.append(dict(name=name,input=data,packets=packets,expected=expected))
    save(out/'cases-and-gold.json',cases)
    save(out/'budget.json',dict(max_calls=2,max_output_tokens=8192,http_timeout=180,retries=0))
    paths=[Path(__file__).resolve(),BASE/'README.md',out/'cases-and-gold.json',out/'budget.json',EXP/'skopos-issue-bridge-v2/envelope.py',EXP/'skopos-issue-bridge-v1/bridge.py',EXP/'issue-store-v1/store.py',EXP/'open-issues-v3/protocol.py',EXP/'review-invariance-v1/transport_diagnostic.py',skopos/'pilot.py',skopos/'export.py']
    frozen={str(p):sha(p) for p in paths};save(out/'freeze.json',frozen)
    report=dict(status='prepared',calls=0,known_tokens=0,cases=[])
    store=storage.Store(out/'issues.sqlite3',create=True)
    try:
        for case in cases:
            stage=out/case['name'];stage.mkdir()
            request=dict(model='glm-5.3-flash',temperature=0,max_tokens=8192,response_format={'type':'json_object'},messages=[dict(role='system',content=storage.protocol.SYSTEM+'\n'+envelope.POLICY),dict(role='user',content=storage.encode(case['input']))])
            save(stage/'request.json',request)
            if any(sha(Path(p))!=v for p,v in frozen.items()):raise ValueError('freeze_changed')
            report.update(status='attempted',calls=report['calls']+1);save(out/'report.json',report)
            # An uncertain outcome is preserved; this runner never resumes or retries.
            start=time.monotonic()
            proc=subprocess.run([sys.executable,str(EXP/'review-invariance-v1/transport_diagnostic.py'),str(stage/'request.json'),'180'],capture_output=True,text=True,timeout=190)
            elapsed=round(time.monotonic()-start,3)
            response=json.loads(proc.stdout);save(stage/'response.json',response)
            usage=(response.get('usage') or {}).get('total_tokens')
            if type(usage) is int:report['known_tokens']+=usage
            if proc.returncode:raise ValueError('transport_failed')
            if response.get('finish_reason')!='stop' or type(usage) is not int:raise ValueError('incomplete_or_unknown_usage')
            assessment=storage.protocol.validate(response['content'],case['input'])
            navigation=[]
            for row in assessment['fields'].values():
                for ref in row['evidence']:
                    hits=envelope.bridge.locate(case['packets'][ref['source_id']],ref['quote'])
                    if not hits:raise ValueError('quote_not_in_selected_literal')
                    navigation.append(dict(reference=ref,locators=hits))
            passed=checks(assessment,case['expected'],case['packets'])
            head=store.append(case['name'],None,case['input'],response['content'],dict(kind='model_candidate',request=request,request_sha256=storage.digest(request),model_reported=response.get('reported_model'),usage=response['usage'],admission='not_admitted'))
            report['cases'].append(dict(name=case['name'],checks=passed,assessment=assessment,navigation=navigation,head=head,seconds=elapsed,usage=response['usage'],reported_model=response.get('reported_model')))
            save(out/'report.json',report)
            # Cases are independent: semantic failure does not suppress the other case.
        store.close();store=storage.Store(out/'issues.sqlite3')
        for case,result in zip(cases,report['cases']):
            record=store.history(case['name'],result['head'])[-1]['record']
            assert [envelope.recover(s) for s in record['input']['sources']]==list(case['packets'].values())
        report.update(status='complete',all_checks_pass=all(all(r['checks'].values()) for r in report['cases']),packets_recovered=True,semantic_review='pending producer review')
    except Exception as exc:
        report.update(status='failed',failure=type(exc).__name__,detail=str(exc)[:160] if isinstance(exc,ValueError) else 'execution_failed',retry='none')
    finally:
        store.close();save(out/'report.json',report);print(json.dumps(report,ensure_ascii=False))
    return 0 if report['status']=='complete' and report['all_checks_pass'] else 2
if __name__=='__main__':raise SystemExit(main())
