"""Local integrity and cost accounting; no semantic verdict inferred."""
from pathlib import Path
import hashlib,json
b=Path(__file__).resolve().parent;p=b/'runs/aspects-01'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
freeze=json.loads((p/'freeze.json').read_text());assert all(sha(p/n)==h for n,h in freeze.items())
for n,h in freeze.items():
 if n.startswith('code/agora/'):assert sha(b.parents[1]/'src/agora'/n.removeprefix('code/agora/'))==h
rows=json.loads((p/'execution.json').read_text());metrics=[]
source=(p/'inputs/source.txt').read_bytes()
for row in rows:
 f=p/row['case']/row['mode']/'result.json';assert sha(f)==row['sha256']
 r=json.loads(f.read_text());assert r['implementation_unchanged']
 for c in r.get('citations',[]):
  for m in c['matches']:assert source[m['start_byte']:m['end_byte']].decode()==c['quote']
 metrics.append(dict(row,source_bytes_sent=sum(len(s['text'].encode()) for s in r.get('envelope',{}).get('spans',[])),prompt_bytes=r.get('prompt_bytes'),usage=r.get('response',{}).get('usage'),citations=len(r.get('citations',[])),answer=r.get('answer')))
result={'integrity_verified':True,'attempted_planned_calls':len(rows)==2,'all_calls_completed':all(x['status']=='complete' for x in rows),'metrics':metrics,'known_tokens':sum(x['tokens'] for x in rows if x['tokens'] is not None),'unknown_usage_calls':sum(x['tokens'] is None for x in rows),'seconds':round(sum(x['seconds'] for x in rows),3),'semantic_review':'separate producer review required'}
with (p/'audit.json').open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False,indent=2))
