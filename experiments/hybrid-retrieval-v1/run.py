import sys,json,hashlib,importlib.util
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
sys.path.insert(0,str(R/'experiments/structure-retrieval-v1'))
from structure import nodes,select
from fusion import fuse
from agora.qasper import render
from agora.source import FileSourceAdapter
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 f=load(B/'freeze.json');assert sha(R/'experiments/structure-retrieval-v1/structure.py')==f['selector_sha256'] and sha(Path(__file__))==f['runner_sha256'];ds=R/'experiments/qasper-v1/inputs/test.json';assert sha(ds)==f['dataset_sha256'];data=load(ds);assert sha(B/'fusion.py')==f['fusion_sha256']
 module=R/'experiments/retrieval-comparison-v1/retrieval_variants.py';assert sha(module)==f['baseline_sha256'];spec=importlib.util.spec_from_file_location('baseline',module);baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline)
 rows=[]
 for c in f['cases']:
  raw,unused=render(data[c['document_id']]);source=R/c['source_path'];assert raw==source.read_bytes() and sha(source)==c['source_sha256'];sections,size=nodes(data[c['document_id']]);assert size==len(raw)
  env=FileSourceAdapter(source,c['document_id']).fetch(c['source_sha256'],[(0,size)],content_budget=size)
  results={'baseline':baseline.select(env,c['question'],[],'exact-paragraphs',12000)}
  results.update({mode:select(raw,c['question'],sections,mode,12000) for mode in ('headings','headings-lists')})
  results['hybrid']=fuse(raw,results['baseline']['ranges'],results['headings-lists']['ranges'],12000)
  rubric=R/c['rubric_path'];assert sha(rubric)==c['rubric_sha256'];gold=load(rubric)['requirements'];unique=sorted({(g['evidence']['start_byte'],g['evidence']['end_byte']) for g in gold})
  for mode,r in results.items():
   assert r['bytes']<=12000
   for a,b in r['ranges']:assert 0<=a<b<=len(raw);raw[a:b].decode()
   hit=[(a,b) for a,b in unique if any(x<=a and b<=y for x,y in r['ranges'])]
   rows.append(dict(case_id=c['id'],mode=mode,covered_paragraphs=len(hit),reference_paragraphs=len(unique),**r))
 return dict(status='complete_not_promoted',provider_calls=0,scope='Four known documents; development test, not new holdout',rows=rows)
if __name__=='__main__':
 r=run()
 if len(sys.argv)>1:
  with Path(sys.argv[1]).open('x') as out:json.dump(r,out,indent=2);out.write('\n')
 for x in r['rows']:print(x['case_id'],x['mode'],x['bytes'],str(x['covered_paragraphs'])+'/'+str(x['reference_paragraphs']))
