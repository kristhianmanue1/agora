"""Known failure follow-up, not a held-out evaluation or automatic retrieval."""
import hashlib,json,runpy
from pathlib import Path
from agora.qasper import render
from expansion import expand
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 previous=BASE.parent/'reviewer-comparison-v2'
 hashes=json.loads((previous/'evidence-sha256.json').read_text())
 for name,h in hashes.items():assert sha((previous/name).read_bytes())==h
 dataset=BASE.parent/'qasper-v1/inputs/test.json'
 assert sha(dataset.read_bytes())==json.loads((previous/'selection.json').read_text())['qasper_sha256']
 paper=json.loads(dataset.read_text())['1811.00051'];source,paragraphs=render(paper)
 relevant=next(p for p in paragraphs if p['text'].startswith('A further limitation of our models'))
 candidates=[p for p in paragraphs if 500<len(p['text'])<2000 and all(t not in p['text'].lower() for t in ('plan','planner','planning','ilp'))]
 control=min(candidates,key=lambda p:abs(len(p['text'])-len(relevant['text'])))
 oldcases={c['id']:c for c in json.loads((previous/'inputs/cases.json').read_text())}
 cases=[];gold={};lineage=[]
 for index in range(2):
  parent=f'long-1811.00051-{index}-abstract';old=oldcases[parent]
  for condition in ('baseline','control','target'):
   expanded=None;evidence=old['evidence']
   if condition!='baseline':
    paragraph=control if condition=='control' else relevant
    expanded=expand(evidence,source,sha(source),paragraph['start_byte'],paragraph['end_byte']);evidence=expanded['evidence']
   for repeat in (1,2):
    cid=f'claim{index}-{condition}-r{repeat}'
    cases.append(dict(id=cid,question=old['question'],claim=old['claim'],evidence=evidence,condition=condition,repeat=repeat,language='en'))
    gold[cid]=('supported' if index==0 else 'contradicted') if condition=='target' else 'insufficient'
    lineage.append(dict(id=cid,parent_case_id=parent,condition=condition,repeat=repeat,parent_evidence_sha256=sha(old['evidence'].encode()),evidence_sha256=sha(evidence.encode()),evidence_bytes=len(evidence.encode()),expansion={k:v for k,v in expanded.items() if k!='evidence'} if expanded else None))
 # Deterministic interleaving; the model sees no condition, repetition or gold.
 cases.sort(key=lambda c:sha(('agora-expansion-01'+c['id']).encode()))
 (BASE/'inputs').mkdir(exist_ok=False)
 for path,data in [(BASE/'inputs/cases.json',cases),(BASE/'gold.json',gold),(BASE/'lineage.json',lineage)]:
  with path.open('x') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
 originals={p:[] for p in ('glm','jev')}
 for provider in originals:
  for line in (previous/('records-'+provider+'.jsonl')).read_text().splitlines():
   r=json.loads(line)
   if r.get('case_id') in [f'long-1811.00051-{i}-abstract' for i in range(2)]:originals[provider].append(r)
  assert len(originals[provider])==2
 (BASE/'originals.json').write_text(json.dumps(originals,indent=2)+'\n')
 (BASE/'parent-hashes.json').write_text(json.dumps({str(previous/name):h for name,h in hashes.items()},indent=2)+'\n')
 print('12 cases per reviewer; relevant/control passage bytes',len(relevant['text'].encode()),len(control['text'].encode()))
if __name__=='__main__':main()
