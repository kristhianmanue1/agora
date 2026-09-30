import json,hashlib,sys
from pathlib import Path
from expansion import expand
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter
from agora.rubric_cli import assess
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=load(B/'freeze.json');case=f['cases'][0];old=B.parent/'reading-paired-grouping-v1';prior=next(c for c in load(old/'freeze.json')['cases'] if c['id']=='selected');source=B/'inputs/expanded.txt';assert sha(source)==case['source_sha256'];assert sha(B/'expansion.py')==f['selector_sha256'];assert sha(B/'inputs/expansion.json')==f['expansion_sha256'];assert sha(old/'selected-rubric.json')==f['original_rubric_sha256']
plan=expand(source.read_bytes(),prior['question'],prior['ranges'],10000,2);assert plan==load(B/'inputs/expansion.json');assert plan['ranges']==case['ranges'];assert plan['delivered_bytes']<=10000
for a,b in prior['ranges']:assert any(x<=a and b<=y for x,y in plan['ranges'])
rubric=load(B/'expanded-rubric.json');assert sha(B/'expanded-rubric.json')==case['rubric_sha256'];assert rubric['requirements'][:2]==load(old/'selected-rubric.json')['requirements'];target=rubric['requirements'][2]['evidence'];assert any(a<=target['start_byte'] and target['end_byte']<=b for a,b in plan['ranges'])
folder=B/'runs-glm/expanded';response=load(folder/'response.json');candidate=load(folder/'candidate.json');replay=query_evidence(FileSourceAdapter(source,'qasper:'+case['document_id']),case['source_sha256'],case['question'],[dict(id='P1',question=case['question'])],lambda *_:response,ranges=case['ranges'],content_budget=60000,prompt_budget=100000,citation_mode='ids',response_language='en',max_unit_bytes=4096);assert replay==candidate
request=load(folder/'request.json');assert request==dict(system=candidate['prompt']['system']+'\n'+f['prompt_addendum'],user=candidate['prompt']['user'])
r=load(B/'runs-review-expanded/result.json');assert r['candidate_sha256']==sha(folder/'candidate.json');assert r['requirements']==assess(r['response'],list(case['expected']))
if (B/'runs-fidelity/expanded.json').exists():
 j=load(B/'runs-fidelity/expanded.json');state=json.loads(j['request']['state']);assert state['claims']==[dict(id='C'+str(i),text=cl['text'],evidence=cl['quotes']) for i,cl in enumerate(candidate['parts'][0]['claims'],1)];assert set(j['response']['answers'])==set(j['request']['questions'])
print('OK: deterministic expansion without reference input, preserved initial context, target recovered, exact unrepaired replay and review bindings; zero HTTP')
