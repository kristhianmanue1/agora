"""Pérdida simulada de confirmación tras commit, en proceso separado, sin red."""
import json
import os
from pathlib import Path
import subprocess
import sys
import recovery as m
BASE=Path(__file__).resolve().parent
f=m.load('recovery_demo_fixture',BASE.parents[0]/'issue-flow-v1/fixtures.py')
def main():
 if sys.argv[1]=='child':
  out=Path(sys.argv[2]);s=m.Store(out/'issues.sqlite3');prepared=json.loads((out/'prepared.json').read_text())
  def provider(*args):
   with (out/'provider-calls.txt').open('a') as stream:stream.write('simulated\n')
   return f.valid_response()
  m.evaluate(s,'recovery-demo-001',prepared,provider);s.close()
  # Se pierde la confirmación de aplicación después de cerrar normalmente SQLite.
  return 7
 os.umask(0o077);out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
 s=m.Store(out/'issues.sqlite3',create=True);data,raw,source=f.inputs();head=s.append('nube',None,data,raw,{'kind':'manual_fixture'})
 prepared=m.flow.prepare(s,'nube',head,source,'2026-10-08');s.close()
 (out/'prepared.json').write_text(json.dumps(prepared))
 child=subprocess.run([sys.executable,str(BASE/'run.py'),'child',str(out)],capture_output=True,text=True,timeout=10)
 if child.returncode!=7 or child.stdout:raise ValueError('unexpected_child_result')
 s=m.Store(out/'issues.sqlite3')
 before=m.inspect(s,'recovery-demo-001')
 def forbidden(*args):raise AssertionError('duplicate_provider_call')
 result=m.evaluate(s,'recovery-demo-001',prepared,forbidden)
 history=s.history('nube',result['revision_sha256']);s.close()
 count=len((out/'provider-calls.txt').read_text().splitlines())
 assert count==1 and len(history)==2 and before['state']=='committed'
 report=dict(status='complete',simulation='application_ack_lost_after_commit',child_exit=child.returncode,child_returned_result=False,operation_id='recovery-demo-001',operation_state=before['state'],recovered_same_result=result==before['result'],revisions=len(history),simulated_provider_calls=count,real_model_calls=0,result=result)
 (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report));return 0
if __name__=='__main__':raise SystemExit(main())
