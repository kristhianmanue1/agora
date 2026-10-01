import json,sys,hashlib,importlib.util
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path[:0]=[str(R/'src'),str(R/'experiments/structure-retrieval-v1'),str(R/'experiments/hybrid-retrieval-v1')]
from structure import nodes,select
from fusion import fuse
from stages import accumulate
from agora.qasper import render
from agora.source import FileSourceAdapter
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 f=load(B/'freeze.json')
 for name,digest in f['implementations'].items():assert sha(R/name)==digest
 ds=R/'experiments/qasper-v1/inputs/test.json';assert sha(ds)==f['dataset_sha256'];data=load(ds)
 spec=importlib.util.spec_from_file_location('baseline',R/'experiments/retrieval-comparison-v1/retrieval_variants.py');baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline);rows=[]
 for c in f['cases']:
  source=R/c['source_path'];raw,_=render(data[c['document_id']]);assert raw==source.read_bytes() and sha(source)==c['source_sha256'];sections,size=nodes(data[c['document_id']]);assert size==len(raw)
  env=FileSourceAdapter(source,c['document_id']).fetch(c['source_sha256'],[(0,size)],content_budget=size);schedule=[]
  for budget in f['budgets']:
   lexical=baseline.select(env,c['question'],[],'exact-paragraphs',budget)
   structural=select(raw,c['question'],sections,'headings-lists',budget)
   combined=fuse(raw,lexical['ranges'],structural['ranges'],budget)
   schedule.append((budget,combined['ranges']))
  history=accumulate(raw,schedule)
  rubric=R/c['rubric_path'];assert sha(rubric)==c['rubric_sha256'];refs=sorted({(g['evidence']['start_byte'],g['evidence']['end_byte']) for g in load(rubric)['requirements']})
  for h in history:h['reference_paragraphs']=len(refs);h['covered_paragraphs']=sum(any(x<=a and b<=y for x,y in h['ranges']) for a,b in refs)
  rows.append(dict(case_id=c['id'],partition=c['partition'],document_id=c['document_id'],history=history))
 return dict(status='complete_not_promoted',provider_calls=0,rows=rows,scope='Known controls and two locally reserved sources; source QASPER structure; no generated answers')
if __name__=='__main__':
 r=run()
 if len(sys.argv)>1:
  with Path(sys.argv[1]).open('x') as out:json.dump(r,out,indent=2);out.write('\n')
 for c in r['rows']:print(c['partition'],c['case_id'],[(h['budget'],h['bytes'],h['covered_paragraphs'],h['reference_paragraphs'],h['stop_reason']) for h in c['history']])
