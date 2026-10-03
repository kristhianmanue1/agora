"""Offline audit of explicit-record preservation and native MemOS extraction."""
import json,hashlib,sys
from pathlib import Path
B=Path(__file__).resolve().parent;load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=load(B/'freeze.json');fixtures=load(B/'fixtures.json')['cases']
assert sha(B/'fixtures.json')==f['fixtures_sha256'] and sha(B/'run_ankla.py')==f['ankla_runner_sha256'] and sha(B/'run_memos.py')==f['runner_sha256']
def nodes(x):
 if isinstance(x,dict):
  if isinstance(x.get('memory'),str):yield x
  else:
   for k,v in x.items():
    if k!='metadata':yield from nodes(v)
 elif isinstance(x,list):
  for y in x:yield from nodes(y)
rows=[];requests=0
for condition in ('record','source'):
 root=B/'runs/ankla'/condition
 verified=load(root/'verify.json');assert verified['exit_code']==0 and json.loads(verified['stdout'])['ok']
 for c in fixtures:
  ident=condition+'-'+c['id'];result=load(root/(c['id']+'-retrieve.json'));assert result['exit_code']==0;r=json.loads(result['stdout']);selected=r['selected'];target=[x for x in selected if x['id']=='test-'+c['id']];assert len(target)==1 and target[0]['render']==c[condition]
  records={}
  for suffix in ('create','add','search','chat'):
   p=B/'runs/memos'/(ident+'-'+suffix+'.json');d=load(p);requests+=1;assert d['status']=='returned' and d['http_status']==200;records[suffix]=d
   for key in ('writable_cube_ids','readable_cube_ids'):
    if key in d['request']:assert d['request'][key] in ([f['cubes'][ident]],[])
  assert records['add']['request']['messages'][0]['content']==c[condition]
  assert records['chat']['request']['add_message_on_answer'] is False and records['chat']['request']['history']==[]
  ns=list(nodes(records['search']['response']['data']['text_mem']))
  rows.append(dict(case=c['id'],condition=condition,expected=c['expected'],ankla=dict(revision=r['revision'],profile=r['profile'],target_rank=next(i+1 for i,x in enumerate(selected) if x['id']=='test-'+c['id']),text_exact=True,returned_records=len(selected),used_bytes=r['used_bytes'],render=target[0]['render']),memos=dict(cube_id=f['cubes'][ident],add_returned_count=len(records['add']['response'].get('data',[])),memories=[dict(id=n['id'],text=n['memory'],type=n.get('metadata',{}).get('memory_type')) for n in ns],answer=records['chat']['response']['data']['response'],ingestion_seconds=records['add']['seconds'],search_seconds=records['search']['seconds'],chat_seconds=records['chat']['seconds'])))
assert requests==f['max_http_requests']
report=dict(status='complete_native_path_diagnostic',rows=rows,http_requests=requests,ankla_external_provider_calls=0,memos_internal_provider_calls='not_measured',memos_tokens_and_cost='not_measured',offline_verified=True,limits=['Different native operations: AN-KLA returns stored text; MemOS extracts and generates. Not a head-to-head generation benchmark.','AN-KLA store has four records per condition; MemOS scopes each case to its own cube. Ranking/noise and isolation are not comparable.','No supersede/refute/checkpoint transition or actual execution-enforcement test performed. Correction is supplied within one input.','Model-derived synthetic summaries, no privileged authority or real approval asserted.','Known synthetic producer labels; no independent adjudication.'],artifact_hashes={str(p.relative_to(B)):sha(p) for p in sorted((B/'runs').rglob('*.json')) if '.an-kla' not in p.parts})
if len(sys.argv)>1:
 with Path(sys.argv[1]).open('x') as h:json.dump(report,h,ensure_ascii=False,indent=2);h.write('\n')
for x in rows:print(x['condition'],x['case'],'AN-KLA rank',x['ankla']['target_rank'],'MemOS memories',len(x['memos']['memories']))
