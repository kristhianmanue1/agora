import json,hashlib,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'));sys.path.insert(0,str(B.parent/'condition-expansion-v1'))
from expansion import expand
from agora.qasper import render
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter
from agora.rubric_cli import assess
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=load(B/'freeze.json');ds=B.parent/'qasper-v1/inputs/test.json';assert sha(ds)==f['dataset_sha256'];data=load(ds);assert sha(B.parent/'condition-expansion-v1/expansion.py')==f['selector_sha256'];assert sha(B/'inputs/inventory.json')==f['inventory_sha256'];initial=f['cases'][0];source=B/'inputs/initial.txt';report=expand(source.read_bytes(),initial['question'],initial['ranges'],10000,2);assert report==load(B/'inputs/expansion.json');assert sha(B/'inputs/expansion.json')==f['expansion_sha256']
for case in f['cases']:
 cid=case['id'];source=B/'inputs'/f'{cid}.txt';assert source.read_bytes()==render(data[case['document_id']])[0];assert case['document_id'] not in f['excluded'];assert sha(source)==case['source_sha256'];assert sha(B/f'{cid}-rubric.json')==case['rubric_sha256'];folder=B/'runs-glm'/cid;c=load(folder/'candidate.json');response=load(folder/'response.json')
 replay=query_evidence(FileSourceAdapter(source,'qasper:'+case['document_id']),case['source_sha256'],case['question'],[dict(id='P1',question=case['question'])],lambda *_:response,ranges=case['ranges'],content_budget=60000,prompt_budget=100000,citation_mode='ids',response_language='en',max_unit_bytes=4096);assert replay==c
 request=load(folder/'request.json');assert request==dict(system=c['prompt']['system']+'\n'+f['prompt_addendum'],user=c['prompt']['user'])
 if c['execution_status']=='complete':
  r=load(B/('runs-review-'+cid)/'result.json');assert r['candidate_sha256']==sha(folder/'candidate.json')
  if r['status']=='complete':assert r['requirements']==assess(r['response'],list(case['expected']))
  j=load(B/'runs-fidelity'/f'{cid}.json');assert set(j['response']['answers'])==set(j['request']['questions']);state=json.loads(j['request']['state']);assert state['claims']==[dict(id='C'+str(i),text=cl['text'],evidence=cl['quotes']) for i,cl in enumerate(c['parts'][0]['claims'],1)]
for test in load(B/'controls.json')['results']:
 raw=test['source'].encode();base=len(b'Datasets Alpha and Beta.');actual=expand(raw,'Which datasets?',[[0,base]],test['report']['total_budget'],2);assert actual==test['report'];assert bool(actual['added'])==test['actual_added'];assert actual['semantic_completeness']=='not_established'
print('OK: frozen heuristic, new source selection, exact candidates, reviewer bindings and all controls reproduced, including known false positive; zero HTTP')
rubric=load(B/'expanded-rubric.json')
for req in rubric['requirements']:
 if req['id'] not in ('R2','R3'):continue
 e=req['evidence'];raw=(B/'inputs/expanded.txt').read_bytes();assert raw[e['start_byte']:e['end_byte']].decode()==e['text']
 for case in f['cases']:assert all(b<=e['start_byte'] or a>=e['end_byte'] for a,b in case['ranges'])
print('OK: both missing metric definitions exist in source and fall outside both delivered contexts')
