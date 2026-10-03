"""Development-only replay; never reads annotations before selecting."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
from agora.qasper import render
from selector import expand
root=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=False)
load=lambda p:json.loads(p.read_text())
sha=lambda raw:hashlib.sha256(raw).hexdigest()
f=load(root/'experiments/comparison-chain-v1/freeze.json')
dataset=(root/'experiments/qasper-v1/inputs/test.json').read_bytes();assert sha(dataset)==f['dataset_sha256'];data=json.loads(dataset)
prior=load(root/'experiments/comparison-chain-v1/selections.json')
freeze={'frozen_at':datetime.now(timezone.utc).isoformat(),'selector_sha256':sha(Path(__file__).with_name('selector.py').read_bytes()),'cases':f['cases'],'dataset_sha256':f['dataset_sha256'],'initial_budget':5000,'expanded_budget':12000,'status':'development_only','http_attempts':0}
(out/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
rows=[]
for case in f['cases']:
 raw,_=render(data[case['id']]);assert sha(raw)==case['sha256']
 start=next(r for r in prior if r['document']==case['id'] and r['method']=='idf' and r['budget']==5000)
 state=dict(source_sha256=sha(raw),question=case['question'],ranges=start['ranges'])
 result=expand(raw,case['question'],state,12000)
 assert set(map(tuple,state['ranges']))<=set(map(tuple,result['ranges']))
 rows.append({'document':case['id'],'question_id':case['question_id'],'initial_bytes':start['bytes'],'initial':state,'expanded':result})
(out/'selections.json').write_text(json.dumps(rows,indent=2)+'\n')
# Annotations only after all retrieval is complete; all cases already development.
for row in rows:
 paper=data[row['document']];raw,_=render(paper)
 qa=next(q for q in paper['qas'] if q['question_id']==row['question_id']);checks=[]
 for a in qa['answers']:
  mapped=[];unmapped=[]
  for evidence in a['answer']['evidence']:
   piece=evidence.strip().encode();start=raw.find(piece) if piece else -1
   if start<0:unmapped.append(evidence)
   else:mapped.append([start,start+len(piece)])
  counts={name:sum(any(c<=a and b<=d for c,d in row[name]['ranges']) for a,b in mapped) for name in ['initial','expanded']}
  checks.append(dict(ranges=mapped,unmapped=unmapped,coverage=counts))
 row['annotations']=checks
(out/'result.json').write_text(json.dumps(rows,indent=2)+'\n')
for row in rows:print(row['document'],row['initial_bytes'],row['expanded']['delivered_bytes'],len(row['expanded']['additions']),[(a['coverage'],len(a['ranges']),len(a['unmapped'])) for a in row['annotations']])
