# Historical selection: rerunning after publication changes the inventory.
import json,re,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'))
from agora.qasper import render,eligible
excluded=set();inventory=[]
for p in (R/'experiments').rglob('*'):
 if not p.is_file() or p.name in ('test.json','train.json','dev.json','validation.jsonl') or p.stat().st_size>2000000 or p.suffix not in ('.json','.jsonl','.md','.py','.txt'):continue
 b=p.read_bytes();excluded.update(re.findall(r'\b\d{4}\.\d{4,5}\b',str(p.relative_to(R))+' '+b.decode(errors='replace')));inventory.append(dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(b).hexdigest()))
data=json.loads((R/'experiments/qasper-v1/inputs/test.json').read_bytes());rows=[]
for pid,paper in data.items():
 if pid in excluded:continue
 raw,paras=render(paper)
 if not 30000<=len(raw)<=60000:continue
 for q in paper['qas']:
  kind,reason=eligible(q,paras)
  if reason or kind!='answerable':continue
  a=q['answers'][0]['answer']
  if not 2<=len(a['extractive_spans'])<=4 or a['free_form_answer']:continue
  if not all(any(s in e for e in a['evidence']) for s in a['extractive_spans']):continue
  rank=hashlib.sha256(('rubric-reserved-v1:'+pid+':'+q['question_id']).encode()).hexdigest();rows.append((rank,pid,q,raw,paras))
rank,pid,q,raw,paras=sorted(rows,key=lambda x:x[0])[0]
Path('/tmp/rubric-selection.json').write_text(json.dumps(dict(document_id=pid,question=q,source_bytes=len(raw),rank=rank,excluded=sorted(excluded),inventory=inventory,eligible_count=len(rows)),indent=2))
print(pid,len(raw),q['question']);print(json.dumps(q['answers'],indent=2))
