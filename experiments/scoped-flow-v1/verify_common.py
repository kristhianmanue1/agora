import json,hashlib
from pathlib import Path
from types import SimpleNamespace
from agora import scoped_rubric as scoped,fidelity_cli as fid,reading_route as route
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify_review(source,rubric,candidate,question,folder,can_expand=False):
 rv=folder/'coverage/result.json';fi=folder/'fidelity/result.json';saved=folder/'route.json';a=SimpleNamespace(source=str(source),source_sha256=sha(source),candidate=str(candidate),candidate_sha256=sha(candidate),rubric=str(rubric),rubric_sha256=sha(rubric),review=str(rv),review_sha256=sha(rv),fidelity=str(fi),fidelity_sha256=sha(fi),question=question,part_id='P1',can_expand=can_expand,out='unused')
 r=load(rv);f=load(fi);c=load(candidate)
 user,req=scoped.prepare(source.read_bytes(),candidate.read_bytes(),rubric.read_bytes(),a)
 if r['status']=='complete':
  assert load(folder/'coverage/request.json')==dict(system=scoped.SYSTEM,user=user)
  assert scoped.assess(r['response'],[x['id'] for x in req['requirements']])==r['requirements']
 if f['status']=='complete':assert f['request']==fid.request(c) and fid.assess(f['response'],f['request'])==f['label']
 assert route.run(a,lambda *x:None)==load(saved)
 return dict(route=load(saved),requirements=r.get('requirements'),fidelity=f.get('label'),coverage_response=r.get('response'),fidelity_response=f.get('response'),http_calls=r['http_attempts']+f['http_attempts'],tokens=r.get('response',{}).get('usage',{}).get('total_tokens',0)+sum(f.get('response',{}).get('usage',{}).get(k,0) for k in ('input_tokens','output_tokens')))
