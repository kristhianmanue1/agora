import json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;P=B.parent/'coverage-cli-long-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=load(P/'freeze.json');source=(P/'inputs/source.txt').read_bytes();assert sha(P/'inputs/source.txt')==f['source_sha256'];rows=[]
for c in f['candidates']:
 method=c['method'];r=load(B/f'runs-{method}/result.json');assert sha(P/'inputs'/f'{method}.json')==c['candidate_sha256'];assert sha(P/f'runs-{method}/result.json')==r['review_sha256']
 for finding in r.get('omissions',[]):
  for e in finding['evidence']:assert source[e['start_byte']:e['end_byte']].decode()==e['text']
 resp=r.get('response',{});rows.append(dict(method=method,status=r['status'],diagnosis_status=r.get('diagnosis_status'),finish_reason=resp.get('finish_reason'),diagnostic=r.get('diagnostic'),omissions=r.get('omissions',[]),usage=resp.get('usage'),model=resp.get('reported_model'),input_hashes_unchanged=True))
result=dict(records=rows,known_tokens=sum(x['usage']['total_tokens'] for x in rows if x['usage']),assessment='Two expected omissions localized; two additional proposals require semantic assessment. Positive live control truncated, not evaluated. No reattempt.',limits='Producer self-review; known single-source development pair; no independent adjudication or semantic precision estimate.');(B/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(result['known_tokens'])
