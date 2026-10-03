"""Offline evidence audit. No inference that HTTP success implies fidelity."""
import json,hashlib,sys,re
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=load(B/'freeze.json')
assert sha(B/'run.py')==f['runner_sha256']
def nodes(x):
 if isinstance(x,dict):
  if isinstance(x.get('memory'),str):yield x
  else:
   for k,v in x.items():
    if k!='metadata':yield from nodes(v)
 elif isinstance(x,list):
  for y in x:yield from nodes(y)
def core(ns):return sorted((n['id'],n['memory']) for n in ns)
rows=[];calls=0
for c in f['cases']:
 source=R/c['source'];assert sha(source)==c['source_sha256'];prefix=c['id']
 def record(suffix):
  global calls
  d=load(B/'runs'/(prefix+'-'+suffix+'.json'));calls+=1;assert d['status']=='returned' and d['http_status']==200 and (d['response'].get('code')==200 if suffix!='chat' else isinstance(d['response'].get('data',{}).get('response'),str))
  request=d['request']
  for key in ('readable_cube_ids','writable_cube_ids','mem_cube_ids'):
   if key in request:assert request[key] in ([c['cube_id']],[])
  return d
 create=record('create');add=record('add');before=record('before');assert add['request']['messages'][0]['content']==source.read_text();searches=[]
 for t in f['relativity_values']:
  d=record('search-'+str(t));ns=list(nodes(d['response']['data']['text_mem']));assert d['request']['query']==c['question'] and d['request']['relativity']==t
  searches.append(dict(relativity=t,count=len(ns),seconds=d['seconds'],memories=[dict(id=n['id'],memory=n['memory'],ref_id=n.get('ref_id'),score=n['metadata'].get('relativity'),source_sha256=n['metadata'].get('source_sha256'),source_text_present=any(s.get('content')==source.read_text() for s in n['metadata'].get('sources',[]) if isinstance(s,dict))) for n in ns]))
 assert len({tuple((m['id'],m['memory']) for m in s['memories']) for s in searches})==1
 assert all(m['source_text_present'] and m['source_sha256']==c['source_sha256'] for s in searches for m in s['memories'])
 chat=record('chat');after=record('after');assert chat['request']['add_message_on_answer'] is False and chat['request']['history']==[] and chat['request']['writable_cube_ids']==[]
 old=list(nodes(before['response']['data']));new=list(nodes(after['response']['data']));assert core(old)==core(new)
 rows.append(dict(id=prefix,cube_id=c['cube_id'],source_sha256=c['source_sha256'],source_bytes=source.stat().st_size,ingestion_seconds=add['seconds'],memories_before=len(old),memories_after=len(new),memory_ids_and_text_unchanged=True,searches=searches,answer=chat['response']['data']['response'],chat_seconds=chat['seconds']))
assert calls==f['max_requests']
q=rows[0];t=rows[1]
assert all(any('Visual7W' in m['memory'] for m in s['memories']) for s in q['searches'])
assert 'Visual7W' in q['answer'] and 'open-domain' in q['answer']
assert 'Wednesday' in t['answer'] and 'Tuesday' in t['answer']
assert not re.search(r'2026|October', (R/f['cases'][1]['source']).read_text())
assert any('October 2, 2026' in m['memory'] for m in t['searches'][0]['memories'])
report=dict(status='complete_mixed_outcomes',rows=rows,http_requests=calls,internal_provider_calls='not_measured',tokens='not_measured',monetary_cost='not_measured',replay_verified=True,source_evaluation='Same-agent inspection; no independent adjudication',findings=['QASPER required answer retrieved at all three thresholds; prior Agora answer omitted Visual7W. Different preprocessing and budgets, no general superiority claim.','Same returned memory IDs/text across thresholds; no evidence here that lowering threshold is necessary.','Temporal day correction retained, but extraction adds meeting date October 2 2026 absent from source, and speculates October 6/7. Calendar speculation is qualified, but origin of meeting date is unsupported.','QASPER extraction added UserMemory inferring personal interests from submitting a paper. This is not an explicit user preference.','Sources metadata contains original text and supplied hash; final Fact references are not verified span-level citations.','Memory IDs/text unchanged before vs after chat; not a claim that all server state is immutable.'],request_hashes={p.name:sha(p) for p in sorted((B/'runs').glob('*.json'))})
if len(sys.argv)>1:
 with Path(sys.argv[1]).open('x') as h:json.dump(report,h,ensure_ascii=False,indent=2);h.write('\n')
print(json.dumps(dict(requests=calls,verified=True,counts=[(x['id'],x['memories_before']) for x in rows],ingestion_seconds=[x['ingestion_seconds'] for x in rows]),ensure_ascii=False))
