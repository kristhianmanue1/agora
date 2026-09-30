# Historical selection procedure: rerunning after new artifacts exist changes inventory.
import json,re,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'));from agora.qasper import render,eligible
excluded=set();files=[]
for p in (R/'experiments').rglob('*'):
 if not p.is_file() or '.git' in p.parts:continue
 if p.name in ('test.json','train.json','dev.json','validation.jsonl') or p.stat().st_size>2000000:continue
 if p.suffix not in ('.json','.jsonl','.md','.py','.txt'):continue
 text=p.read_text(errors='replace');excluded.update(re.findall(r'\b\d{4}\.\d{4,5}\b',str(p.relative_to(R))+' '+text));files.append(str(p.relative_to(R)))
data=json.loads((R/'experiments/qasper-v1/inputs/test.json').read_text());candidates=[]
for pid,paper in data.items():
 if pid in excluded:continue
 raw,paras=render(paper)
 if not 20000<=len(raw)<=65000:continue
 for q in paper['qas']:
  kind,reason=eligible(q,paras)
  if reason:continue
  a=q['answers'][0]['answer']
  if kind=='answerable' and not(a['free_form_answer'] or len(a['extractive_spans'])>=2):continue
  rank=hashlib.sha256(('coverage-heldout-v1:'+pid+':'+q['question_id']).encode()).hexdigest();candidates.append((rank,pid,kind,q,raw))
chosen=[];seen=set()
for kind,n in [('answerable',4),('unanswerable',2)]:
 for rank,pid,k,q,raw in sorted(candidates):
  if k!=kind or pid in seen:continue
  chosen.append(dict(document_id=pid,question_id=q['question_id'],kind=k));seen.add(pid)
  print(pid,k,q['question'])
  for a in q['answers']:print({k:v for k,v in a['answer'].items() if k not in ('evidence','highlighted_evidence')})
  if sum(x['kind']==kind for x in chosen)==n:break
Path('/tmp/agora-reserved-selection.json').write_text(json.dumps(dict(selected=chosen,excluded=sorted(excluded),inventory_files=files),indent=2))
