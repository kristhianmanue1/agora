"""Offline preservation check; no provider invocation."""
from pathlib import Path
import hashlib,json,sys
p=Path(__file__).resolve().parent;root=p.parents[1];sys.path.insert(0,str(root/'src'))
from agora.relation_candidates import validate
load=lambda name:json.loads((p/name).read_text())
f=load('freeze.json');raw=(p/'source.txt').read_bytes()
assert hashlib.sha256(raw).hexdigest()==f['source_sha256']
assert raw==(root/'experiments/relation-real-v1/source.txt').read_bytes()
g=load('generation/result.json');r=load('review/result.json');c=load('generation/candidate.json')
assert validate(raw,f['source_id'],c)==g['assessment']==r['structural_assessment']
assert c['schema']=='agora/relation-candidate/v2'
assert c['fields']['software_version']=={'text':None,'evidence_ids':[]}
assert c['fields']['model_configuration']['text']=='big version of hyper parameters'
assert c['fields']['input']['text'] is None
assert r['review']['software_version']==r['review']['input']=='insufficient'
assert not r['admitted'] and not r['review_inconsistencies']
assert g['provider_calls']==r['provider_calls']==1
assert g['response']['usage']['total_tokens']+r['response']['usage']['input_tokens']+r['response']['usage']['output_tokens']==7137
print('OK: v2 bindings and unknowns preserved; 7137 observed tokens; semantics not certified')
