import json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;P=B.parent/'coverage-cli-long-v1';OLD=B.parent/'omission-cli-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=load(P/'freeze.json');source=(P/'inputs/source.txt').read_bytes();assert sha(P/'inputs/source.txt')==f['source_sha256'];records=[]
for c in f['candidates']:
 method=c['method'];r=load(B/f'runs-{method}/result.json');request=load(B/f'runs-{method}/request.json');assert request==load(OLD/f'runs-{method}/request.json');assert sha(P/'inputs'/f'{method}.json')==c['candidate_sha256'];assert sha(P/f'runs-{method}/result.json')==r['review_sha256'];assert r['request_config']['max_tokens']==4096
 for finding in r.get('omissions',[]):
  for e in finding['evidence']:assert source[e['start_byte']:e['end_byte']].decode()==e['text']
 response=r.get('response',{});records.append(dict(method=method,status=r['status'],diagnosis_status=r.get('diagnosis_status'),diagnostic=r.get('diagnostic'),review_disagreement=r.get('review_disagreement'),finish_reason=response.get('finish_reason'),omissions=r.get('omissions',[]),usage=response.get('usage'),model=response.get('reported_model'),old_result_sha256=sha(OLD/f'runs-{method}/result.json'),request_unchanged=True))
out=dict(records=records,known_tokens=sum(x['usage']['total_tokens'] for x in records if x['usage']),limits='One draw per candidate, known development pair, larger output budget but same prompts; no general causal or semantic reliability claim. Original attempts retained.');(B/'result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
