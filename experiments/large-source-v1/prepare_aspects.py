"""Experimental question decomposition, no semantic coverage guarantee."""
from pathlib import Path
import hashlib,json
from agora.source import FileSourceAdapter,digest
from agora.passages import lexical_ranges
b=Path(__file__).resolve().parent;out=b/'runs/aspects-01';out.mkdir(parents=True,exist_ok=False)
f=b/'inputs/source.txt';adapter=FileSourceAdapter(f,'qasper:1810.13414');raw=f.read_bytes();full=adapter.fetch(digest(raw),[(0,len(raw))],content_budget=160000)
aspects=[('names','method extract natural language names Web ranking'),('plans','method extract sentence plans Web ranking'),('selection','human selection ranking candidate'),('evaluation','evaluation outcome full automation'),('manual','remaining manually authored resources text plans'),('language','languages other than English future work')]
selected=set();rows=[]
for aid,query in aspects:
 ranges,meta=lexical_ranges(full,query,2000,top_k=1)
 selected.update(tuple(x) for x in ranges)
 rows.append({'id':aid,'query':query,'ranges':ranges,'retrieval':meta,'semantic_coverage':'not_verified'})
assert sum(e-s for s,e in selected)<=12000
# One bounded expansion per aspect, preserving earlier selection; no LLM judge.
expansion=[]
for aid,query in aspects:
 ranges,_=lexical_ranges(full,query,4000,top_k=2)
 added=[]
 for s,e in ranges:
  if (s,e) not in selected and sum(y-x for x,y in selected)+e-s<=12000:
   selected.add((s,e));added.append([s,e])
 expansion.append({'id':aid,'added':added})
record={'source_sha256':digest(raw),'budget_bytes':12000,'initial_per_aspect_bytes':2000,'expanded_per_aspect_bytes':4000,'aspects':rows,'expansion':expansion,'ranges':sorted(selected),'selected_bytes':sum(e-s for s,e in selected),'semantic_coverage':'not_verified','decomposition':'producer supplied from question; case previously observed; not automatic or independent','local_scan':'12 lexical scans of full source; no LLM extraction calls'}
(out/'selection.json').write_text(json.dumps(record,indent=2)+'\n')
for s,e in sorted(selected):print(s,e,raw[s:e].decode()[:140])
print('selected_bytes',record['selected_bytes'])
