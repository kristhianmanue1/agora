"""Demostración sin red: abierto, resuelto, reapertura parcial; reinicios reales."""
import hashlib
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
from store import Store,protocol,PROTOCOL
BASE=Path(__file__).resolve().parent
V3=BASE.parents[0]/'open-issues-v3'

def raw(fields,reason):return json.dumps(dict(fields=fields,reason=reason),ensure_ascii=False)
def field(value,support,source,quote,relation,requirement):
 return dict(observed_value=value,support_status=support,missing_requirements=[] if value else [requirement],relations=[relation],change_source_ids=[],evidence=[dict(source_id=source,quote=quote)])
def steps():
 case=next(c for c in json.loads((V3/'cases.json').read_text()) if c['id']=='partial_refutation')
 p0=dict(id='p0',text='Coordinación: fecha y responsable de Nube están pendientes.',received_at='2026-09-30')
 p0['sha256']=hashlib.sha256(p0['text'].encode()).hexdigest()
 initial=protocol.payload(case,0);initial.update(sources=[p0],dependents=[],as_of='2026-09-30')
 a=raw({k:field(None,'missing','p0',p0['text'],'initial',k+'_confirmed') for k in ('date','owner')},'Pendientes ambos datos; fixture manual.')
 resolved=protocol.payload(case,0);resolved.update(sources=[case['sources'][0]],dependents=[],as_of='2026-10-01')
 b=raw(dict(date=field('2026-10-21','supported','p1','Nube se entrega el 2026-10-21','initial','date_confirmed'),owner=field('Lina','supported','p1','Lina es responsable','initial','owner_confirmed')),'Datos definidos en p1; fixture manual.')
 results=json.loads((V3/'result-glm-01.json').read_text())
 result=next(x['result'] for x in results['assessments'] if x['case']=='partial_refutation' and x['mode']=='full')
 c=raw(result['fields'],result['reason'])
 return [(initial,a,{'kind':'manual_fixture'}),(resolved,b,{'kind':'manual_fixture'}),(protocol.payload(case,0),c,{'kind':'replayed_model_assessment','source':'open-issues-v3/result-glm-01.json','source_sha256':hashlib.sha256((V3/'result-glm-01.json').read_bytes()).hexdigest(),'model_reported':'glm-5.3-flash','new_model_call':False})]

def main():
 if len(sys.argv)>1 and sys.argv[1]=='read':
  s=Store(sys.argv[2]);history=s.history('nube',sys.argv[3]);s.close();print(json.dumps(history,ensure_ascii=False));return
 os.umask(0o077)
 out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
 (out/'code').mkdir()
 for path in (BASE/'store.py',BASE/'run.py',PROTOCOL):shutil.copyfile(path,out/'code'/path.name)
 db=out/'issues.sqlite3';s=Store(db,create=True);s.close()
 parent=None;reports=[]
 for data,response,origin in steps():
  s=Store(db);parent=s.append('nube',parent,data,response,origin);before=s.history('nube',parent);s.close()
  # Proceso nuevo: sin conexión SQLite ni objetos anteriores en memoria.
  process=subprocess.run([sys.executable,str(BASE/'run.py'),'read',str(db),parent],capture_output=True,text=True,check=True,timeout=10)
  recovered=json.loads(process.stdout)
  if recovered!=before:raise ValueError('reopen_mismatch')
  reports.append(dict(revision=len(recovered),digest=parent,status=recovered[-1]['record']['assessment']['status'],reopened_fields=recovered[-1]['record']['assessment']['reopened_fields'],fresh_process_exact_recovery=True))
 report=dict(revisions=reports,model_calls=0,source_mode='synthetic_manual_and_replay',expected_statuses=['open','resolved','partial'],observed_statuses=[r['status'] for r in reports],code_sha256={str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/'store.py',BASE/'run.py',PROTOCOL)})
 if report['observed_statuses']!=report['expected_statuses']:raise ValueError('unexpected_transition')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
