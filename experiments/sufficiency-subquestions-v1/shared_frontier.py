import json,re,sys,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'src'))
from agora.passages import terms
from agora.subquestions import merge_ranges
from agora.source import FileSourceAdapter
b=r/'experiments/sufficiency-subquestions-v1';parent=r/'experiments/sufficiency-real-retrieval-v1';specs=json.loads((b/'specifications.json').read_text());reports=json.loads((b/'retrieval.json').read_text())
protocol=dict(status='post-baseline development comparison, not reserved validation',rule='Keep union; rank missing immediate seed neighbors by overlap with subquestion, descending score then document order; append those fitting shared budget; one frontier, no target-specific terms',budget_bytes=8000,provider_calls=0)
(b/'shared-protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');rows=[]
for d,spec in zip(reports,specs):
 source=parent/'inputs'/f"{d['document_id']}.txt";data=source.read_bytes();plan=json.loads((b/'inputs'/f"{d['document_id']}-plan.json").read_text());blocks=[];offset=0
 for block in re.split(r'(?:\r?\n){2,}',data.decode()):
  raw=block.encode()
  if raw:
   start=data.find(raw,offset);blocks.append((start,start+len(raw),block));offset=start+len(raw)
 current=[(s['start_byte'],s['end_byte']) for s in plan['envelope']['spans']];candidates={}
 for q,report in zip(spec['questions'],plan['questions']):
  for seed in report['retrieval']['seed_paragraphs']:
   for i in (seed-1,seed+1):
    if 0<=i<len(blocks):
     a,z,t=blocks[i]
     if not any(x<=a and y>=z for x,y in current):candidates[i]=max(candidates.get(i,0),len(terms(t)&terms(q['query'])))
 additions=[];skipped=[]
 for i,score in sorted(candidates.items(),key=lambda x:(-x[1],x[0])):
  a,z,t=blocks[i];proposal=merge_ranges(current+[(a,z)])
  if sum(y-x for x,y in proposal)<=8000:current=proposal;additions.append(dict(paragraph=i,start_byte=a,end_byte=z,score=score,sha256=hashlib.sha256(t.encode()).hexdigest()))
  else:skipped.append(i)
 env=FileSourceAdapter(source,'qasper:'+d['document_id']).fetch(d['source_sha256'],[tuple(x) for x in merge_ranges(current)],content_budget=8000)
 assert all(any(x['start_byte']<=s['start_byte'] and x['end_byte']>=s['end_byte'] for x in env['spans']) for s in plan['envelope']['spans'])
 assert all(data[s['start_byte']:s['end_byte']].decode()==s['text'] for s in env['spans'])
 (b/'inputs'/f"{d['document_id']}-shared-envelope.json").write_text(json.dumps(env,ensure_ascii=False,indent=2)+'\n')
 joined='\n'.join(s['text'] for s in env['spans']);rows.append(dict(document_id=d['document_id'],before_bytes=d['after_bytes'],after_bytes=env['delivered_bytes'],additions=additions,skipped=skipped,contains_denoising='denois' in joined.lower(),contains_entity_evaluation='xie16entitydesc2' in joined,contains_five_languages=all(v in joined for v in ['Arabic','Chinese','French','English','German']),existing_ranges_preserved=True))
(b/'shared-result.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
