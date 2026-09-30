import json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;load=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest();receipt=load(B/'receipt.json');old=B.parent/'omission-cli-budget-v2/runs-shared/result.json';raw=old.read_bytes();assert sha(raw)==receipt['original_result_sha256'];original=load(old)['response']['content'].encode();derived=load(B/'inputs/response.json')['content'].encode();assert original==derived+b'`';assert sha(original)==receipt['original_content_sha256'];assert sha(derived)==receipt['derived_content_sha256'];assert receipt['operation']['offset']==len(derived);assert sha((B/'inputs/response.json').read_bytes())==receipt['derived_response_sha256']
r=load(B/'result.json');live=load(B/'runs-replay/result.json');assert sha((B/'runs-replay/result.json').read_bytes())==r['replay_result_sha256'];assert live['status']=='complete' and live['origin']=='replay' and live['http_attempts']==0 and live['review_disagreement'];assert r['omissions']==live['omissions'];P=B.parent/'coverage-cli-long-v1';source=(P/'inputs/source.txt').read_bytes();assert sha(source)==live['source_sha256'];assert sha((P/'inputs/shared.json').read_bytes())==live['candidate_sha256'];assert sha((P/'runs-shared/result.json').read_bytes())==live['review_sha256']
for f in live['omissions']:
 for e in f['evidence']:assert source[e['start_byte']:e['end_byte']].decode()==e['text']
assessment=load(B/'assessment.json');assert len(assessment['findings'])==len(live['omissions'])==2
for a in assessment['findings']:
 e=live['omissions'][a['proposal_index']]['evidence'][0];assert a['source_range']==[e['start_byte'],e['end_byte']]
print('Exact one-byte derivative; hashes and offsets valid; replay no HTTP; originals unchanged')
