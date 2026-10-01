"""Final development comparison; frozen policy, offline, no promotion."""
import json,hashlib,sys,importlib.util
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1]
sys.path[:0]=[str(R/'src'),str(R/'experiments/structure-retrieval-v1')]
from structure import nodes,select
from agora.qasper import render
from agora.source import FileSourceAdapter
from agora.subquestions import merge_ranges
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 f=load(B/'freeze.json')
 for n,h in f['bindings'].items():assert sha(R/n)==h,n
 data=load(R/'experiments/qasper-v1/inputs/test.json')
 spec=importlib.util.spec_from_file_location('baseline',R/'experiments/retrieval-comparison-v1/retrieval_variants.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
 rows=[]
 for c in f['cases']:
  src=R/c['source_path'];raw,_=render(data[c['document_id']]);assert raw==src.read_bytes() and sha(src)==c['source_sha256']
  sections,size=nodes(data[c['document_id']]);assert size==len(raw)
  env=FileSourceAdapter(src,c['document_id']).fetch(c['source_sha256'],[(0,size)],content_budget=size)
  lexical=base.select(env,c['question'],[],'exact-paragraphs',20000)
  structural=select(raw,c['question'],sections,'headings-lists',20000)
  chosen=merge_ranges(lexical['ranges']);skipped=[]
  for pair in structural['ranges']:
   proposed=merge_ranges(chosen+[pair])
   if sum(b-a for a,b in proposed)<=20000:chosen=proposed
   else:skipped.append(pair)
  assert all(any(a<=x and y<=b for a,b in chosen) for x,y in lexical['ranges'])
  assert sum(b-a for a,b in chosen)<=20000
  for a,b in chosen:raw[a:b].decode()
  rubric=R/c['rubric_path'];assert sha(rubric)==c['rubric_sha256']
  refs=sorted({(x['evidence']['start_byte'],x['evidence']['end_byte']) for x in load(rubric)['requirements']})
  def score(rs):return sum(any(a<=x and y<=b for a,b in rs) for x,y in refs)
  rows.append(dict(id=c['id'],document_id=c['document_id'],references=len(refs),baseline_covered=score(lexical['ranges']),alternative_covered=score(chosen),baseline_bytes=sum(b-a for a,b in lexical['ranges']),alternative_bytes=sum(b-a for a,b in chosen),ranges=chosen,skipped=skipped))
 return dict(scope=f['scope'],rows=rows,provider_calls=0,baseline_ranges_preserved=True,promotion='not_performed',phase_recommendation='close_experimental_phase_with_known_limits')
if __name__=='__main__':
 r=run()
 if len(sys.argv)>1:
  with Path(sys.argv[1]).open('x') as h:json.dump(r,h,indent=2);h.write('\n')
 for x in r['rows']:print(x['id'],x['baseline_covered'],x['alternative_covered'],x['references'],x['alternative_bytes'])
