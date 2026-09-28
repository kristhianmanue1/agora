"""Paquete sintético real del exportador Skopos; proveedor de evaluación simulado."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from bridge import convert,locate,digest
BASE=Path(__file__).resolve().parent
EXPERIMENTS=BASE.parent

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
 skopos=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();os.umask(0o077);out.mkdir(parents=True,exist_ok=False)
 pilot=load('skopos_bridge_pilot',skopos/'experiments/meeting-source-v1/pilot.py')
 export=load('skopos_bridge_export',skopos/'experiments/meeting-source-v1/export.py')
 recovery=load('bridge_recovery',EXPERIMENTS/'issue-recovery-v1/recovery.py')
 fixtures=load('bridge_fixtures',EXPERIMENTS/'issue-flow-v1/fixtures.py')
 source=dict(source_id='meeting-nube-synthetic',revision=1,supersedes=None,complete=False,segments=[dict(id='decision',start_ms=1000,end_ms=9000,speaker='Coordinación sintética',text='Coordinación confirma: Nube se entrega el 2026-10-21. Lina sigue siendo responsable.')])
 src=out/'meeting.json';src.write_text(json.dumps(source,ensure_ascii=False))
 producer=pilot.MeetingStore();producer.ingest(src);packet=export.export_packet(producer,['Nube'])
 incoming,receipt=convert(packet,'2026-10-08',producer.fetch)
 (out/'packet.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2));(out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
 store=recovery.Store(out/'issues.sqlite3',create=True);data,raw,_=fixtures.inputs();head=store.append('nube',None,data,raw,{'kind':'manual_fixture'})
 prepared=recovery.flow.prepare(store,'nube',head,incoming,'2026-10-08')
 calls=[]
 def provider(system,user):
  calls.append(1);response=fixtures.valid_response();content=json.loads(response['content'])
  for row in content['fields'].values():
   for ref in row['evidence']:ref['source_id']=incoming['id']
  response['content']=json.dumps(content);return response
 result=recovery.evaluate(store,'skopos-bridge-001',prepared,provider)
 navigation=[]
 for row in result['assessment']['fields'].values():
  for ref in row['evidence']:navigation.append(dict(quote=ref['quote'],locators=locate(packet,ref['quote'])))
 store.close();store=recovery.Store(out/'issues.sqlite3')
 def forbidden(*args):raise AssertionError('duplicate_call')
 recovered=recovery.evaluate(store,'skopos-bridge-001',prepared,forbidden);history=store.history('nube',result['revision_sha256']);store.close()
 assert recovered==result and len(history)==2 and len(calls)==1
 assert receipt['capture_complete_declared'] is False and receipt['selection_complete']=='not_established'
 report=dict(status='complete',source=receipt,navigation=navigation,operation_recovered=True,revisions=2,simulated_provider_calls=1,real_model_calls=0,skopos_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=skopos,text=True).strip(),skopos_code_sha256={n:hashlib.sha256((skopos/'experiments/meeting-source-v1'/n).read_bytes()).hexdigest() for n in ('pilot.py','export.py')},assessment=result['assessment'],packet_sha256=digest(packet),limitation='synthetic export, simulated evaluator; packet/receipt kept alongside SQLite, not embedded in issue history')
 (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
