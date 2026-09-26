"""Verify receipts and anchors without inferring semantic success."""
from pathlib import Path
import hashlib,json
b=Path(__file__).resolve().parent;p=b/'runs/glm-01';root=b.parents[1]
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
manifest=json.loads((p/'freeze.json').read_text());assert all(sha(p/n)==h for n,h in manifest.items())
for n,h in manifest.items():
 if n.startswith('code/agora/'):assert sha(root/'src/agora'/n.removeprefix('code/agora/'))==h
rows=json.loads((p/'execution.json').read_text());details=[]
for row in rows:
 f=p/row['kind']/row['case']/'result.json';assert sha(f)==row['sha256'];r=json.loads(f.read_text());assert r['implementation_unchanged']
 source=(p/'inputs'/(row['case']+'.txt')).read_bytes()
 for anchor in r.get('citations',[]):
  assert anchor['matches']
  for m in anchor['matches']:assert source[m['start_byte']:m['end_byte']].decode()==anchor['quote']
 details.append(dict(row,answer_status=r.get('answer_status'),citations=len(r.get('citations',[])),parts=r.get('parts'),answer=r.get('answer'),semantic_support=r.get('semantic_support')))
summary={'attempts':len(rows),'planned':6,'all_attempted':len(rows)==6,'accepted':sum(x['status']=='complete' for x in rows),'known_tokens':sum(x['tokens'] for x in rows if x['tokens'] is not None),'unknown_usage_calls':sum(x['tokens'] is None for x in rows),'seconds':round(sum(x['seconds'] for x in rows),3),'integrity_verified':True,'details':details}
with (p/'audit.json').open('x') as f:json.dump(summary,f,ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False,indent=2))
