"""Reconstruct public inputs from frozen selection; no provider calls."""
import json,hashlib,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.qasper import render
sha=lambda b:hashlib.sha256(b).hexdigest()
f=json.loads((B/'freeze.json').read_text());raw=(B.parent/'qasper-v1/inputs/test.json').read_bytes();assert sha(raw)==f['dataset_sha256']
paper=json.loads(raw)[f['document_id']];source,_=render(paper);assert sha(source)==f['source_sha256']
q=next(q for q in paper['qas'] if q['question_id']==f['question_id']);rubric=json.loads((B/'rubric.json').read_text());assert sha((B/'rubric.json').read_bytes())==f['rubric_sha256']
state=dict(task=q['question'],full_source=source.decode(),requirements=rubric['requirements'],reference_annotations=[a['answer'] for a in q['answers']])
cases=(json.dumps([dict(id='rubric-blind-review',state=state)],ensure_ascii=False,indent=2)+'\n').encode();assert sha(cases)==f['review_cases_sha256']
p=B/'inputs';p.mkdir(exist_ok=True)
for name,content in [('source.txt',source),('cases.json',cases)]:
 target=p/name
 if target.exists():assert target.read_bytes()==content
 else:target.write_bytes(content)
print('Public source and blind review payload reproduced; zero HTTP')
