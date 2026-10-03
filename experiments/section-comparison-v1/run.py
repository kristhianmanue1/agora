"""Frozen offline section comparison; annotations used only after retrieval."""
import argparse,json,hashlib,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args();sys.path.insert(0,str(args.repo/'src'))
from agora.qasper import render
from agora.source import FileSourceAdapter,digest
from agora.passages import lexical_ranges
from agora.structure_selection import nodes,select
from agora.subquestions import merge_ranges
f=json.loads(Path(__file__).with_name('freeze.json').read_text());dataset=(args.repo/'experiments/qasper-v1/inputs/test.json').read_bytes();assert digest(dataset)==f['dataset_sha256'];data=json.loads(dataset);args.out.mkdir(exist_ok=False)
rows=[];sources={}
# Complete every selection before consulting answer annotations.
for case in f['cases']:
 paper=data[case['id']];raw,paragraphs=render(paper);assert digest(raw)==case['sha256'];sections,size=nodes(paper);assert size==len(raw);sources[case['id']]=raw
 path=args.out/(case['id']+'.txt');path.write_bytes(raw);adapter=FileSourceAdapter(path,case['id']);full=adapter.fetch(case['sha256'],[(0,len(raw))],content_budget=100000)
 for q in case['questions']:
  for budget in f['budgets']:
   for method in f['methods']:
    if method in ['overlap','idf']:ranges,details=lexical_ranges(full,q['question'],budget,f['top_k'],ranking=method)
    else:details=select(raw,q['question'],sections,method,budget);ranges=details['ranges']
    ranges=merge_ranges(ranges);size=sum(b-a for a,b in ranges);assert size<=budget
    for a,b in ranges:raw[a:b].decode()
    rows.append(dict(document=case['id'],question_id=q['id'],question=q['question'],known=case['known'],budget=budget,method=method,delivered_bytes=size,ranges=ranges,selection_details=details))
(args.out/'selections.json').write_text(json.dumps(rows,indent=2)+'\n')
manual=json.loads((args.repo/'experiments/focused-label-v1/repair/case.json').read_text())
references={}
for case in f['cases']:
 raw=sources[case['id']]
 for q in case['questions']:
  if case['known']:groups=[{'type':'manual','evidence':[r['text'] for r in manual['ranges']]}]
  else:
   qa=next(x for x in data[case['id']]['qas'] if x['question_id']==q['id'])
   groups=[dict(type='qasper_annotation',unanswerable=a['answer'].get('unanswerable'),evidence=a['answer'].get('evidence',[])) for a in qa['answers']]
  mapped=[]
  for g in groups:
   spans=[];unmapped=[]
   for e in g['evidence']:
    piece=e.strip().encode();a=raw.find(piece) if piece else -1
    if a<0:unmapped.append(e)
    else:spans.append([a,a+len(piece)])
   mapped.append(dict(type=g['type'],unanswerable=g.get('unanswerable'),ranges=spans,unmapped=unmapped,expected_evidence_count=len(g['evidence'])))
  references[(case['id'],q['id'])]=mapped
for row in rows:
 checks=[]
 for g in references[(row['document'],row['question_id'])]:
  complete=sum(any(c<=a and b<=d for c,d in row['ranges']) for a,b in g['ranges'])
  checks.append(dict(mapped=len(g['ranges']),unmapped=len(g['unmapped']),complete=complete,unanswerable=g['unanswerable'],all_evidence_covered=(complete==len(g['ranges'])) if g['ranges'] and not g['unmapped'] else None))
 row['reference_coverage']=checks
result=dict(schema='aria/section-comparison/v1',http_attempts=0,rows=rows,reference_basis='manual known case and QASPER annotation evidence, no generated answer accuracy',limits=['two documents new to scanned experiment artifacts only','multiple annotations scored separately','unmapped and unanswerable preserved','heading selector ranks three sections, lexical selects six seeds: same bytes, different policy','no semantic review or default promotion'])
(args.out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(args.out/'references.json').write_text(json.dumps([dict(document=k[0],question_id=k[1],annotations=v) for k,v in references.items()],ensure_ascii=False,indent=2)+'\n')
for r in rows:print(r['document'],r['question_id'][:6],r['budget'],r['method'],r['delivered_bytes'],[(x['complete'],x['mapped'],x['unmapped']) for x in r['reference_coverage']])
