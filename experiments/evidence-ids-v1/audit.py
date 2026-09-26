"""Verify paired inputs, evidence IDs, expanded quotes, integrity and cost."""
from pathlib import Path
import hashlib,json
from agora.evidence_ids import build_units
b=Path(__file__).resolve().parent;p=b/'runs/glm-01';root=b.parents[1]
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
frozen=json.loads((p/'freeze.json').read_text());assert all(sha(p/n)==h for n,h in frozen.items())
for n,h in frozen.items():
 if n.startswith('code/agora/'):assert sha(root/'src/agora'/n.removeprefix('code/agora/'))==h
cases={c['id']:c for c in json.loads((p/'inputs/cases.json').read_text())};rows=json.loads((p/'execution.json').read_text());details=[]
for row in rows:
 f=p/row['mode']/row['case']/'result.json';assert sha(f)==row['sha256'];r=json.loads(f.read_text());assert r['implementation_unchanged']
 raw=(p/'inputs'/cases[row['case']]['source']).read_bytes()
 for s in r.get('envelope',{}).get('spans',[]):assert raw[s['start_byte']:s['end_byte']].decode()==s['text']
 if row['mode']=='ids' and 'evidence_units' in r:
  assert r['evidence_units']==build_units(r['envelope'],r['source_id'],r['source_sha256'])
  units={u['id']:u for u in r['evidence_units']}
 for a in r.get('citations',[]):
  for m in a['matches']:assert raw[m['start_byte']:m['end_byte']].decode()==a['quote']
  if row['mode']=='ids':
   u=units[a['evidence_id']];assert a['quote']==u['text'];assert a['matches']==[{'start_byte':u['start_byte'],'end_byte':u['end_byte']}]
 if row['mode']=='ids':
  other=p/'literal'/row['case']/'result.json'
  if other.exists():
   old=json.loads(other.read_text());assert r.get('envelope')==old.get('envelope') and r.get('requested_aspects')==old.get('requested_aspects')
 details.append(dict(row,citations=len(r.get('citations',[])),expanded_quote_bytes=sum(len(a['quote'].encode()) for a in r.get('citations',[])),prompt_tokens=r.get('response',{}).get('usage',{}).get('prompt_tokens'),completion_tokens=r.get('response',{}).get('usage',{}).get('completion_tokens'),parts=r.get('parts')))
scores={}
for mode in ('literal','ids'):
 subset=[x for x in details if x['mode']==mode]
 scores[mode]={'attempts':len(subset),'accepted':sum(x['status']=='complete' for x in subset),'known_tokens':sum(x['tokens'] for x in subset if x['tokens'] is not None),'unknown_usage':sum(x['tokens'] is None for x in subset),'seconds':round(sum(x['seconds'] for x in subset),3),'expanded_quote_bytes':sum(x['expanded_quote_bytes'] for x in subset)}
record={'integrity_verified':True,'all_attempted':len(rows)==8,'scores':scores,'details':details,'semantic_review':'separate producer review, not inferred from ID validity'}
with (p/'audit.json').open('x') as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps(scores,indent=2))
