import json,hashlib,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.qasper import render
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();dump=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
old=B.parent/'rubric-reserved-v1';f=load(old/'freeze.json');dataset=B.parent/'qasper-v1/inputs/test.json';assert sha(dataset)==f['dataset_sha256'];paper=load(dataset)[f['document_id']];source,paras=render(paper);assert hashlib.sha256(source).hexdigest()==f['source_sha256'];assert sha(old/'rubric.json')==f['rubric_sha256'];rubric=load(old/'rubric.json');q=next(q for q in paper['qas'] if q['question_id']==f['question_id'])
(B/'inputs').mkdir();(B/'.gitignore').write_text('inputs/\nruns-*/\n')
units=[dict(p,id='S'+str(i)) for i,p in enumerate(paras,1)]
state=dict(task=rubric['question'],requirements=rubric['requirements'],source_units=units,reference_annotations=[a['answer'] for a in q['answers']]);dump(B/'inputs/cases.json',[dict(id='localized-critique',state=state)]);dump(B/'inputs/units.json',units)
dump(B/'freeze.json',dict(source_sha256=f['source_sha256'],rubric_sha256=f['rubric_sha256'],cases_sha256=sha(B/'inputs/cases.json'),max_calls=dict(glm=1,jev=1),max_glm_output_tokens=4096,timeout_seconds=90,retries=0,prior_label_hidden=True,candidates_absent=True,stop_rule='No malformed-response repair, no retries, no automatic rubric edits or candidate generation. Findings require source-ID validation and separate provider assessment. New assessments cannot explain the internal cause of the original verdict.',selection='Same original reserved case; now diagnostic development, not a second held-out case.'))
