import json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();p=B/'freeze.json';f=json.loads(p.read_text());(B/'selection-freeze.json').write_bytes(p.read_bytes())
for c in f['cases']:c.update(source_path=str(B.relative_to(B.parents[1])/'inputs'/f"{c['id']}.txt"),rubric_path=str(B.relative_to(B.parents[1])/f"{c['id']}-rubric.json"),format='QASPER rendered text')
fixtures=[('markdown','.md','# Deployment note\n\n## Window\nThe deployment window is Tuesday at 10:00 UTC.\n\n## Rollback\nRollback requires an error rate above 2% for ten minutes.\n','When is deployment and what triggers rollback?',['The deployment window is Tuesday at 10:00 UTC.','Rollback requires an error rate above 2% for ten minutes.']),('jsonl','.jsonl','{"time":"09:00","speaker":"Coordinator","text":"Draft date: Tuesday."}\n{"time":"09:15","speaker":"Coordinator","text":"Correction: Wednesday; Tuesday is cancelled."}\n','What is the final date and what changed?',['Correction: Wednesday; Tuesday is cancelled.'])]
for cid,ext,text,question,answers in fixtures:
 source=B/'inputs'/(cid+ext);source.write_text(text);raw=source.read_bytes();req=[]
 for i,answer in enumerate(answers,1):
  a=raw.index(answer.encode());req.append(dict(id='R'+str(i),requirement=answer,evidence=dict(text=answer,start_byte=a,end_byte=a+len(answer.encode()))))
 rubric=B/(cid+'-rubric.json');rubric.write_text(json.dumps(dict(schema='agora/task-rubric/v1-experimental',source_sha256=sha(source),question=question,provenance='New synthetic fixture, producer labels; no real meeting or operational instruction',requirements=req),indent=2)+'\n')
 f['cases'].append(dict(id=cid,document_id='synthetic-'+cid,question=question,source_path=str(source.relative_to(B.parents[1])),rubric_path=str(rubric.relative_to(B.parents[1])),source_sha256=sha(source),rubric_sha256=sha(rubric),format=ext+' raw UTF-8'))
f.update(max_http_calls=12,generation_tokens=8192,review_tokens=2048,retries=0,reading_budget=20000,scope='Two locally new QASPER documents plus new synthetic Markdown and JSONL; raw UTF-8, not PDF/Word parsing',stop_rule='One generation, one scoped coverage review and one fidelity review per valid case; no retries, repairs, substitution or budget changes')
p.write_text(json.dumps(f,indent=2)+'\n');(B/'.gitignore').write_text('inputs/\nruns/\n')
