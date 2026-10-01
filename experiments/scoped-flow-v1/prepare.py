import json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
(B/'inputs').mkdir();(B/'.gitignore').write_text('inputs/\nruns/\n')
raw=b'Meeting opened.\n\nThe deadline is Friday.';source=B/'inputs/control.txt';source.write_bytes(raw);question='What is the deadline?';e=dict(text='The deadline is Friday.',start_byte=17,end_byte=len(raw));rub=dict(schema='agora/task-rubric/v1-experimental',source_sha256=sha(raw),question=question,provenance='Producer synthetic control, fixed labels before execution',requirements=[dict(id='R1',requirement='Identify the deadline.',evidence=e)]);dump(B/'control-rubric.json',rub)
rows=[]
for name,status,text,expected,full in [('scoped-absence','not_in_passages','The deadline is not stated in the supplied passages.','missing',False),('omission','answered','Meeting opened.','missing',True),('contradiction','answered','The deadline is Monday.','contradicted',True),('covered','answered','The deadline is Friday.','covered',True),('global-denial','answered','The source does not specify a deadline.','contradicted',True)]:
 span=dict(start_byte=0,end_byte=len(raw) if full else 15,text=raw.decode() if full else 'Meeting opened.')
 part=dict(id='P1',status=status,claims=[] if status=='not_in_passages' else [dict(text=text,quotes=['Meeting opened.' if name=='omission' else e['text']])],missing=[text] if status=='not_in_passages' else [])
 candidate=dict(schema='agora/claim-evidence-query/v2',execution_status='complete',source_id='control',source_sha256=sha(raw),envelope=dict(spans=[span]),parts=[part]);path=B/'inputs'/f'{name}.json';dump(path,candidate)
 rows.append(dict(id=name,source=str(source.relative_to(R)),source_sha256=sha(raw),question=question,candidate=str(path.relative_to(R)),candidate_sha256=sha(path.read_bytes()),rubric=str((B/'control-rubric.json').relative_to(R)),rubric_sha256=sha((B/'control-rubric.json').read_bytes()),expected=expected))
dump(B/'controls-freeze.json',dict(cases=rows,max_calls=5,max_tokens=2048,retries=0,stop_rule='No editing or retrying controls after response; preserve all labels'))
