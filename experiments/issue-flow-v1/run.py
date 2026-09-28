"""Un caso GLM, una solicitud, conservación de fallos y recuperación nueva."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from adapter import Store,prepare,evaluate_and_record,STORE_PATH,store_module
from fixtures import inputs
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 if sys.argv[1]=='read':
  s=Store(sys.argv[2]);result=s.history('nube',sys.argv[3]);s.close();print(json.dumps(result));return 0
 os.umask(0o077);out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
 paths=[BASE/n for n in ('adapter.py','fixtures.py','run.py','README.md')]+[STORE_PATH,store_module.PROTOCOL,ROOT/'experiments/review-invariance-v1/transport_diagnostic.py']
 for p in paths:shutil.copyfile(p,out/p.name)
 save(out/'budget.json',dict(max_calls=1,max_output_tokens=8192,http_timeout=180,process_timeout=190,retries=0,model='glm-5.3-flash'))
 frozen={p.name:sha(p) for p in out.iterdir()};save(out/'freeze.json',frozen)
 s=Store(out/'issues.sqlite3',create=True);data,raw,new=inputs()
 head=s.append('nube',None,data,raw,{'kind':'manual_fixture'})
 prepared=prepare(s,'nube',head,new,'2026-10-08');save(out/'prepared.json',prepared)
 report=dict(status='prepared',model_calls=0,base_head=head);save(out/'report.json',report)
 def provider(system,user):
  if any(sha(out/n)!=v for n,v in frozen.items()):raise ValueError('frozen_file_changed')
  req=dict(model='glm-5.3-flash',temperature=0,max_tokens=8192,response_format={'type':'json_object'},messages=[dict(role='system',content=system),dict(role='user',content=user)])
  save(out/'request.json',req);report.update(status='attempted',model_calls=1);save(out/'report.json',report)
  start=time.monotonic()
  try:
   proc=subprocess.run([sys.executable,str(out/'transport_diagnostic.py'),str(out/'request.json'),'180'],capture_output=True,text=True,timeout=190)
   response=json.loads(proc.stdout);save(out/'response.json',response)
   report['usage']=response.get('usage');report['reported_model']=response.get('reported_model')
   if proc.returncode or 'transport_error' in response:raise ValueError('transport_failed')
   return response
  finally:report['seconds']=round(time.monotonic()-start,3);save(out/'report.json',report)
 try:
  result=evaluate_and_record(s,prepared,provider);save(out/'candidate.json',result)
  history=s.history('nube',result['revision_sha256']);s.close();s=None
  proc=subprocess.run([sys.executable,str(BASE/'run.py'),'read',str(out/'issues.sqlite3'),result['revision_sha256']],capture_output=True,text=True,timeout=10,check=True)
  recovered=json.loads(proc.stdout)
  if recovered!=history:raise ValueError('reopen_mismatch')
  assessment=result['assessment'];correct=assessment['status']=='resolved' and {k:v['observed_value'] for k,v in assessment['fields'].items()}=={'date':'2026-10-21','owner':'Lina'}
  report.update(status='complete',revisions=len(recovered),exact_recovery_new_process=True,expected_values_match=correct,result=result)
 except Exception as exc:
  report.update(status='failed',failure_type=type(exc).__name__,failure=str(exc)[:120] if isinstance(exc,ValueError) else 'execution_failed')
 finally:
  if s is not None:s.close()
  report['frozen_files_verified']=all(sha(out/n)==v for n,v in frozen.items());save(out/'report.json',report);print(json.dumps(report))
 return 0 if report['status']=='complete' and report['expected_values_match'] and report['frozen_files_verified'] else 2
if __name__=='__main__':raise SystemExit(main())
