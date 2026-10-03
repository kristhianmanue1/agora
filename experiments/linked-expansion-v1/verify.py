"""Offline frozen development replay; no providers."""
import hashlib,json
from pathlib import Path
from agora.qasper import render
from selector import expand
here=Path(__file__).resolve().parent;root=here.parents[1]
load=lambda name:json.loads((here/name).read_text())
sha=lambda raw:hashlib.sha256(raw).hexdigest()
f=load('freeze.json');raw=(root/'experiments/qasper-v1/inputs/test.json').read_bytes()
assert sha(raw)==f['dataset_sha256']
assert sha((here/'selector.py').read_bytes())==f['selector_sha256']
data=json.loads(raw);selections=load('selections.json');results=load('result.json')
assert len(selections)==len(results)==4
for saved,scored in zip(selections,results):
 assert all(scored[k]==v for k,v in saved.items())
 case=next(c for c in f['cases'] if c['id']==saved['document'])
 source,_=render(data[case['id']]);assert sha(source)==case['sha256']
 result=expand(source,case['question'],saved['initial'],f['expanded_budget'])
 assert result==saved['expanded']
 assert set(map(tuple,saved['initial']['ranges']))<=set(map(tuple,result['ranges']))
 assert result['delivered_bytes']<=f['expanded_budget']
 for a in scored['annotations']:
  for key in ['initial','expanded']:
   assert a['coverage'][key]==sum(any(c<=x and y<=d for c,d in saved[key]['ranges']) for x,y in a['ranges'])
print('OK: four frozen expansions reproduced; preserved ranges and annotation arithmetic; no semantic certification')
