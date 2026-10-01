import json,re,hashlib,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.qasper import render,eligible
sha=lambda b:hashlib.sha256(b).hexdigest();dump=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
excluded=set();inventory=[]
for p in (R/'experiments').rglob('*'):
 if not p.is_file() or B in p.parents or p.name in ('test.json','train.json','dev.json','validation.jsonl') or p.stat().st_size>2000000 or p.suffix not in ('.json','.jsonl','.md','.py','.txt'):continue
 raw=p.read_bytes();excluded.update(re.findall(r'\b\d{4}\.\d{4,5}\b',str(p.relative_to(R))+' '+raw.decode(errors='replace')));inventory.append(dict(path=str(p.relative_to(R)),sha256=sha(raw)))
ds=B.parent/'qasper-v1/inputs/test.json';data=json.loads(ds.read_bytes());rows=[]
for pid,paper in data.items():
 if pid in excluded:continue
 source,paras=render(paper)
 if not 30000<=len(source)<=60000:continue
 for q in paper['qas']:
  kind,reason=eligible(q,paras)
  if reason or kind!='answerable':continue
  a=q['answers'][0]['answer']
  if not 2<=len(a['extractive_spans'])<=4 or a['free_form_answer'] or not all(any(x in e for e in a['evidence']) for x in a['extractive_spans']):continue
  rows.append((sha(('staged-retrieval-v1:'+pid+':'+q['question_id']).encode()),pid,q,source,paras))
selected=[];seen=set()
for row in sorted(rows,key=lambda r:r[0]):
 if row[1] in seen:continue
 selected.append(row);seen.add(row[1])
 if len(selected)==2:break
assert len(selected)==2
(B/'inputs').mkdir(exist_ok=True);(B/'.gitignore').write_text('inputs/\nruns-*/\n');dump(B/'inputs/inventory.json',inventory);cases=[]
for i,(rank,pid,q,source,paras) in enumerate(selected,1):
 cid='case-'+str(i);(B/'inputs'/f'{cid}.txt').write_bytes(source);a=q['answers'][0]['answer'];req=[]
 for j,text in enumerate(a['extractive_spans'],1):
  evidence=next(p for p in paras if text.strip() in p['text'] and any(p['text'].strip()==e.strip() for e in a['evidence']));req.append(dict(id='R'+str(j),requirement='Include this reference-answer information, allowing equivalent phrasing: '+text.strip(),evidence=evidence))
 rubric=dict(schema='agora/task-rubric/v1-experimental',source_sha256=sha(source),question=q['question'],provenance='Producer extraction from first human QASPER annotation, frozen before generation; not independently adjudicated.',requirements=req);dump(B/f'{cid}-rubric.json',rubric);dump(B/'inputs'/f'{cid}-annotations.json',q['answers'])
 cases.append(dict(id=cid,document_id=pid,question_id=q['question_id'],question=q['question'],source_sha256=sha(source),source_bytes=len(source),source_words=len(source.decode().split()),rubric_sha256=sha((B/f'{cid}-rubric.json').read_bytes()),expected={x['id']:'covered' for x in req},selection_rank=rank));print(cid,pid,len(source),q['question'],a['extractive_spans'])
base=json.loads((B.parent/'citation-grouping-v1/freeze.json').read_text());dump(B/'freeze.json',dict(cases=cases,dataset_sha256=sha(ds.read_bytes()),excluded=sorted(excluded),inventory_sha256=sha((B/'inputs/inventory.json').read_bytes()),inventory_files=len(inventory),eligible_count=len(rows),selection_scope='Local experiment inventory <=2MB, excluding raw datasets; no claim about model training or other exposure.',prompt_addendum=None,initial_budget=8000,initial_top_k=4,recovery_budget=12000,recovery_top_k=3,following=3,recovery_query='Exact original question; no rubric-derived terms',generation_tokens=4096,review_tokens=2048,max_unit_bytes=4096,max_http_calls=12,timeout_seconds=90,retries=0,stop_rule='No retries, candidate repair, rubric edits or reselection. Failed generation skips its reviewers but does not skip the other case. Defaults unchanged.',success='Report structural validity, rubric coverage and separate-provider fidelity separately. No promotion from two cases alone. Full reading; no savings claim.'))
