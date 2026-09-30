"""Replay generation validation and verify bindings without network."""
import json,hashlib,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter
from agora.qasper import render
from agora.rubric_cli import assess
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=load(B/'freeze.json');ds=B.parent/'qasper-v1/inputs/test.json';assert sha(ds)==f['dataset_sha256'];data=load(ds)
assert sha(B/'inputs/inventory.json')==f['inventory_sha256'];assert sha(B/'inputs/fidelity/cases.json')==load(B/'fidelity-freeze.json')['cases_sha256']
for case in f['cases']:
 cid=case['id'];source=B/'inputs'/f'{cid}.txt';assert case['document_id'] not in f['excluded'];assert source.read_bytes()==render(data[case['document_id']])[0];assert sha(source)==case['source_sha256'];rubric=load(B/f'{cid}-rubric.json');assert sha(B/f'{cid}-rubric.json')==case['rubric_sha256'];assert rubric['question']==case['question']
 for item in rubric['requirements']:
  e=item['evidence'];assert source.read_bytes()[e['start_byte']:e['end_byte']].decode()==e['text']
 folder=B/'runs-glm'/cid;c=load(folder/'candidate.json');response=load(folder/'response.json');replay=query_evidence(FileSourceAdapter(source,'qasper:'+case['document_id']),case['source_sha256'],case['question'],[dict(id='P1',question=case['question'])],lambda *_:response,ranges=case['ranges'],content_budget=60000,prompt_budget=100000,citation_mode='ids',response_language='en',max_unit_bytes=4096);assert replay==c
 request=load(folder/'request.json');assert request==dict(system=c['prompt']['system']+'\n'+f['prompt_addendum'],user=c['prompt']['user'])
 if c['execution_status']=='complete':
  r=load(B/('runs-review-'+cid)/'result.json');assert r['candidate_sha256']==sha(folder/'candidate.json') and r['rubric_sha256']==case['rubric_sha256'];assert r['requirements']==assess(r['response'],list(case['expected']));assert r['disposition']=='requires_review'
  j=load(B/'runs-fidelity'/f'{cid}.json');assert set(j['request']['questions'])==set(j['response']['answers']);state=json.loads(j['request']['state']);assert 'coverage' not in state and 'requirements' not in state
  assert state['claims']==[dict(id='C'+str(i),text=cl['text'],evidence=cl['quotes']) for i,cl in enumerate(c['parts'][0]['claims'],1)]
print('OK: one reserved source with two reading arms, public sources, rubric locators, exact unrepaired replay, effective prompts and blinded fidelity bindings; zero HTTP')

from agora.subquestions import prepare_subquestions
selected=next(c for c in f['cases'] if c['id']=='selected')
plan=prepare_subquestions(FileSourceAdapter(B/'inputs/selected.txt','qasper:'+selected['document_id']),selected['source_sha256'],dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='P1',query=selected['question'],reference_ranges=[])]),budget=8000,top_k=4,strategy='paragraphs-equal')
assert json.loads(json.dumps(plan))==load(B/'inputs/selection-plan.json');assert sha(B/'inputs/selection-plan.json')==f['selection_plan_sha256']
result=load(B/'result.json');e=result['posthoc_producer_finding']['evidence'];assert (B/'inputs/full.txt').read_bytes()[e['start_byte']:e['end_byte']].decode()==e['text']
assert not any('Automotive' in s['text'] for s in plan['envelope']['spans'])
print('OK: selection reproduced from question alone, gap locator verified; no reference-answer oracle')
