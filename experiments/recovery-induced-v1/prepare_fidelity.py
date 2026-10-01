import json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for case in load(B/'freeze.json')['cases']:
 for arm,relative in [('derived','derived/result.json')]:
  p=B/'runs'/case['id']/relative
  if not p.exists():continue
  c=load(p)
  if c['execution_status']!='complete':continue
  part=c['parts'][0];state=dict(task=case['question'],claims=[dict(id='C'+str(i),text=cl['text'],evidence=cl['quotes']) for i,cl in enumerate(part['claims'],1)],missing=part['missing'])
  if part['missing']:state['full_source_for_missing_only']='\n\n'.join(s['text'] for s in c['envelope']['spans'])
  rows.append(dict(id=case['id']+'-'+arm,state=state,candidate_sha256=sha(p)))
(B/'inputs/fidelity').mkdir(exist_ok=False)
p=B/'inputs/fidelity/cases.json';p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
with (B/'fidelity-freeze.json').open('x') as out:json.dump(dict(cases_sha256=sha(p),max_calls=len(rows),coverage_labels_hidden=True),out,indent=2)
print('Fidelity cases:',len(rows))
