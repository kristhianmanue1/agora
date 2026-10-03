"""Verify derived-source provenance and preserved relation artifacts offline."""
import hashlib,json,sys
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[1];sys.path.insert(0,str(root/'src'))
from agora.relation_candidates import validate
load=lambda name:json.loads((p/name).read_text());sha=lambda raw:hashlib.sha256(raw).hexdigest()
f=load('freeze.json');source=(p/'source.txt').read_bytes();assert sha(source)==f['source_sha256']
request=json.loads((root/'experiments/streaming-diagnosis-v1/request.json').read_text());original=json.loads(request['state'])['paper'].encode();assert sha(original)==f['original_source_sha256']
for mapping in f['mapping']:
 a,b=mapping['derived_range'];c,d=mapping['original_range']
 assert source[a:b]==original[c:d]
 assert sha(source[a:b])==mapping['text_sha256']
original_run=load('generation/result.json');assert original_run['execution_status']=='rejected'
repair=load('repair-receipt.json');repaired=load('repaired-response.json')
assert sha(original_run['response']['content'].encode())==repair['original_content_sha256']
assert sha(repaired['content'].encode())==repair['derived_content_sha256']
assert original_run['response']['content'].endswith('\n`')
assert repaired['content']==original_run['response']['content'][:-1]
g=load('repaired-generation/result.json');candidate=load('repaired-generation/candidate.json')
assert g['origin']=='supplied_response_replay'
assert g['response']==repaired
assert g['execution_status']=='complete' and g['provider_calls']==1
assert validate(source,f['source_id'],candidate)==g['assessment']
r=load('review/result.json');assert r['execution_status']=='complete' and r['provider_calls']==1
assert r['structural_assessment']==g['assessment']
assert not r['admitted'] and r['semantic_support']=='not_verified'
assert r['candidate_sha256']==sha(json.dumps(candidate,sort_keys=True).encode())
assert json.loads(g['prompt']['user'])['question']==f['question']
print('OK: derived spans map to original revision; candidate and review bound; no semantic certification')

assert original_run['response']['usage']['total_tokens'] + r['response']['usage']['input_tokens'] + r['response']['usage']['output_tokens'] == 6969
