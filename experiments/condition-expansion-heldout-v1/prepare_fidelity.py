import json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;load=lambda p:json.loads(p.read_text());dump=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');f=load(B/'freeze.json');rows=[]
for case in f['cases']:
 p=B/'runs-glm'/case['id']/'candidate.json';c=load(p)
 if c['execution_status']!='complete':continue
 part=c['parts'][0];state=dict(task=case['question'],claims=[dict(id='C'+str(i),text=cl['text'],evidence=cl['quotes']) for i,cl in enumerate(part['claims'],1)],missing=part['missing'])
 if part['missing']:state['full_source_for_missing_only']='\n\n'.join(s['text'] for s in c['envelope']['spans'])
 rows.append(dict(id=case['id'],state=state,candidate_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(B/'inputs/fidelity').mkdir(exist_ok=False);dump(B/'inputs/fidelity/cases.json',rows);dump(B/'fidelity-freeze.json',dict(cases_sha256=hashlib.sha256((B/'inputs/fidelity/cases.json').read_bytes()).hexdigest(),max_calls=len(rows),coverage_labels_hidden=True,criteria_origin='Existing supported/contradicted/insufficient distinction; per-claim assessment against its own citations.'))
print('Frozen fidelity checks:',len(rows))
