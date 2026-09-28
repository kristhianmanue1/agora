"""Use the existing retriever; measure the known target only after selection."""
import hashlib,json
from pathlib import Path
from agora.passages import prepare as retrieve
from agora.source import FileSourceAdapter
BASE=Path(__file__).resolve().parent

def recover(adapter,revision,question,claim,budget):
 query=question+'\n'+claim
 envelope,metadata,_=retrieve(adapter,revision,query,'retrieve',content_budget=budget,top_k=3)
 return query,envelope,metadata

def main():
 previous=BASE.parent/'reviewer-comparison-v2'
 rows={c['id']:c for c in json.loads((previous/'inputs/cases.json').read_text())}
 full=rows['long-1811.00051-0-full']['evidence'].encode();revision=hashlib.sha256(full).hexdigest()
 declared=next(d for d in json.loads((previous/'selection.json').read_text())['documents'] if d['paper_id']=='1811.00051')
 assert revision==declared['sha256']
 out=BASE/'inputs';out.mkdir(exist_ok=False);(out/'source.txt').write_bytes(full)
 adapter=FileSourceAdapter(out/'source.txt','qasper:1811.00051')
 cases=[];selections=[]
 for index in range(2):
  parent=f'long-1811.00051-{index}-abstract';old=rows[parent]
  for budget in (4096,8192):
   query,envelope,metadata=recover(adapter,revision,old['question'],old['claim'],budget)
   spans=envelope['spans'] if envelope else []
   evidence=old['evidence']+''.join('\n\n'+span['text'] for span in spans if span['text']!=old['evidence'])
   cid=f'claim{index}-budget{budget}'
   cases.append(dict(id=cid,question=old['question'],claim=old['claim'],evidence=evidence,language='en'))
   selections.append(dict(id=cid,parent_case_id=parent,query=query,budget=budget,source_sha256=revision,source_bytes=len(full),retrieval=metadata,ranges=[{k:span[k] for k in ('start_byte','end_byte','sha256')} for span in spans],retrieved_bytes=sum(len(s['text'].encode()) for s in spans),evidence_bytes=len(evidence.encode()),evidence_sha256=hashlib.sha256(evidence.encode()).hexdigest()))
 # No target information was loaded or consulted before recovery above.
 prior=json.loads((BASE.parent/'evidence-expansion-v1/lineage.json').read_text())
 target=next(r['expansion'] for r in prior if r['condition']=='target')
 for selection in selections:
  selection['known_target_contained']=any(r['start_byte']<=target['start_byte'] and r['end_byte']>=target['end_byte'] for r in selection['ranges'])
 for path,value in [(out/'cases.json',cases),(BASE/'selection.json',selections)]:
  with path.open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
 for s in selections:print(json.dumps({k:s[k] for k in ('id','retrieved_bytes','evidence_bytes','known_target_contained')}))
if __name__=='__main__':main()
