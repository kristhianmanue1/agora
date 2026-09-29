"""Offline validation of frozen shared-neighbor rule; no provider calls."""
import hashlib,json,re,sys,time,subprocess,random,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from agora.passages import terms
from agora.subquestions import merge_ranges,prepare_subquestions
from agora.source import FileSourceAdapter
from agora.qasper import render,eligible
B=ROOT/'experiments/shared-neighbor-validation-v1'
def sha(x):return hashlib.sha256(x).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def expand(data,plan,spec,budget):
 blocks=[];offset=0
 for text in re.split(r'(?:\r?\n){2,}',data.decode()):
  raw=text.encode()
  if raw:
   start=data.find(raw,offset);blocks.append((start,start+len(raw),text));offset=start+len(raw)
 current=[(s['start_byte'],s['end_byte']) for s in (plan['envelope'] or {}).get('spans',[])];candidates={}
 for q,report in zip(spec['questions'],plan['questions']):
  for seed in report['retrieval']['seed_paragraphs']:
   for i in (seed-1,seed+1):
    if 0<=i<len(blocks):
     a,z,t=blocks[i]
     if not any(x<=a and y>=z for x,y in current):candidates[i]=max(candidates.get(i,0),len(terms(t)&terms(q['query'])))
 for i,score in sorted(candidates.items(),key=lambda x:(-x[1],x[0])):
  a,z,_=blocks[i];proposal=merge_ranges(current+[(a,z)])
  if sum(y-x for x,y in proposal)<=budget:current=proposal
 return merge_ranges(current)
def spec(queries):return dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id=f'q{i}',query=q,reference_ranges=[]) for i,q in enumerate(queries)])
def execute(source,data,sp,budget):
 source.write_bytes(data);adapter=FileSourceAdapter(source,'validation:source');revision=sha(data)
 plan=prepare_subquestions(adapter,revision,sp,budget=budget,top_k=3)
 ranges=expand(data,plan,sp,budget);env=adapter.fetch(revision,[tuple(x) for x in ranges],content_budget=budget) if ranges else None
 before=[(s['start_byte'],s['end_byte']) for s in (plan['envelope'] or {}).get('spans',[])]
 assert sum(z-a for a,z in ranges)<=budget
 assert all(any(x<=a and y>=z for x,y in ranges) for a,z in before)
 assert all(a<z and (i==0 or ranges[i-1][1]<a) for i,(a,z) in enumerate(ranges))
 if env:
  for s in env['spans']:assert data[s['start_byte']:s['end_byte']].decode()==s['text']
 assert ranges==expand(data,plan,sp,budget)
 return plan,env,ranges

def main():
 global B
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--protocol',type=Path,required=True);args=parser.parse_args();previous=json.loads(args.protocol.read_text());B=args.out.resolve()
 B.mkdir();(B/'inputs').mkdir();started=time.monotonic()
 # Establish corpus exclusion before adding new artifacts.
 excluded={'1911.10742'};files=[]
 for p in (ROOT/'experiments').rglob('*.json'):
  if B in p.parents or p.stat().st_size>2000000 or any(x in p.name for x in ('test','dataset')):continue
  if 'inputs' in p.parts and p.name not in ('cases.json','selection.json'):continue
  ids=set(re.findall(r'\b\d{4}\.\d{4,5}\b',p.read_text(errors='replace')))
  if ids:excluded|=ids;files.append(str(p.relative_to(ROOT)))
 dataset_path=ROOT/'experiments/qasper-v1/inputs/test.json';raw=dataset_path.read_bytes();expected=json.loads((dataset_path.parent/'provenance.json').read_text())['test.json']['sha256'];assert sha(raw)==expected;dataset=json.loads(raw)
 candidates=[]
 for pid,paper in dataset.items():
  if pid in excluded:continue
  data,paras=render(paper)
  if not 20000<=len(data)<=65000:continue
  for qa in paper['qas']:
   kind,reason=eligible(qa,paras)
   if kind=='answerable' and reason is None and 1<=len(qa['question'])<=1700:
    candidates.append((sha(('shared-validation-v1:'+pid+':'+qa['question_id']).encode()),pid,qa['question_id']));break
 chosen=[('',x['document_id'],x['question_id']) for x in previous['selected']];assert len(chosen)==12;assert previous['dataset_sha256']==expected
 protocol=dict(code_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dataset_sha256=expected,seed='shared-validation-v1',selection='first eligible answerable question per unseen document; rank sha256(seed:pid:qid); 20k..65k rendered bytes; 12 documents',excluded=sorted(excluded),exclusion_files=files,selected=[dict(document_id=p,question_id=q) for _,p,q in chosen],budgets=[4000,8000],top_k=3,queries='original question plus Which methods, data, conditions and results support the answer to: + original question',primary='All byte-bound, budget, preservation and deterministic checks must pass; report utility descriptively without declaring general semantic completeness.',utility='annotated-paragraph coverage and fraction of retrieved bytes inside annotated evidence; annotations only scored after selection, never supplied to retriever',provider_calls=0,limitations='development query expansion, not autonomous decomposition; local exclusions not proof of no unrecorded exposure; QASPER evidence is incomplete proxy')
 protocol['replay_of']=str(args.protocol.resolve());protocol['exclusions_at_original_selection']=previous['excluded'];dump(B/'protocol.json',protocol)
 # Equivalence to the two original pilot outputs.
 eq=[];old=ROOT/'experiments/sufficiency-subquestions-v1';specs=json.loads((old/'specifications.json').read_text());oldrows=json.loads((old/'retrieval.json').read_text())
 for row,sp in zip(oldrows,specs):
  pid=row['document_id'];data=(ROOT/'experiments/sufficiency-real-retrieval-v1/inputs'/f'{pid}.txt').read_bytes();plan=json.loads((old/'inputs'/f'{pid}-plan.json').read_text());actual=expand(data,plan,sp,8000);env=json.loads((old/'inputs'/f'{pid}-shared-envelope.json').read_text());assert actual==[[s['start_byte'],s['end_byte']] for s in env['spans']];eq.append(pid)
 checks=[]
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'source.txt'
  fixtures=[('utf8','áéí 猫 😀\n\nneedle evaluación\n\nniño costo €'.encode(),['needle','evaluación'],70),('duplicates',b'needle\n\nrepeat\n\nneedle\n\nrepeat',['needle','needle'],20),('no-match',b'alpha\n\nbeta',['zzz','zzz'],20),('no-space',b'needle\n\nneighbor',['needle'],6),('oversized',b'x'*300+b' needle\n\nshort',['needle'],25),('crlf','á\r\n\r\nneedle\r\n\r\n猫'.encode(),['needle'],20)]
  for name,data,queries,budget in fixtures:
   plan,env,ranges=execute(p,data,spec(queries),budget)
   if name in ('no-match','oversized'):assert not ranges
   if name=='no-space':assert ranges==[[0,6]]
   checks.append(name)
  rng=random.Random(29102026)
  for i in range(200):
   blocks=[' '.join(rng.choices(['needle','noise','éxito','猫','😀','repeat'],k=rng.randint(1,15))) for _ in range(rng.randint(2,25))];data='\n\n'.join(blocks).encode();budget=rng.randint(2,max(2,len(data)));execute(p,data,spec(['needle','éxito']),budget)
  rows=[]
  for _,pid,qid in chosen:
   paper=dataset[pid];data,paras=render(paper);qa=next(q for q in paper['qas'] if q['question_id']==qid);sp=spec([qa['question'],'Which methods, data, conditions and results support the answer to: '+qa['question']]);refs=[]
   for a in qa['answers']:
    for evidence in a['answer']['evidence']:
     par=next(x for x in paras if x['text'].strip()==evidence.strip());refs.append((par['start_byte'],par['end_byte']))
   refs=merge_ranges(refs)
   for budget in [4000,8000]:
    start=time.monotonic();plan,env,ranges=execute(p,data,sp,budget);elapsed=time.monotonic()-start;before=[(s['start_byte'],s['end_byte']) for s in (plan['envelope'] or {}).get('spans',[])];count=lambda rs:sum(any(x<=a and y>=z for x,y in rs) for a,z in refs)
    overlap=lambda rs:sum(max(0,min(y,z)-max(x,a)) for x,y in rs for a,z in refs)
    rows.append(dict(document_id=pid,question_id=qid,budget=budget,source_bytes=len(data),source_words=len(data.decode().split()),source_sha256=sha(data),reference_ranges=refs,reference_count=len(refs),before_ranges=before,after_ranges=ranges,before_bytes=sum(z-a for a,z in before),after_bytes=sum(z-a for a,z in ranges),before_covered=count(before),after_covered=count(ranges),before_annotated_overlap_bytes=overlap(before),after_annotated_overlap_bytes=overlap(ranges),elapsed_seconds=elapsed))
 summary=[]
 for budget in [4000,8000]:
  rr=[x for x in rows if x['budget']==budget];v=dict(budget=budget,documents=len(rr),improved_documents=sum(x['after_covered']>x['before_covered'] for x in rr),equal_documents=sum(x['after_covered']==x['before_covered'] for x in rr),regressed_documents=sum(x['after_covered']<x['before_covered'] for x in rr),references=sum(x['reference_count'] for x in rr))
  for key in ['before_bytes','after_bytes','before_covered','after_covered','before_annotated_overlap_bytes','after_annotated_overlap_bytes']:v[key]=sum(x[key] for x in rr)
  summary.append(v)
 result=dict(pilot_equivalence=eq,edge_cases=checks,randomized_cases=200,invariants_passed=True,provider_calls=0,summary=summary,records=rows,total_seconds=time.monotonic()-started)
 dump(B/'result.json',result);(B/'.gitignore').write_text('inputs/\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}))
if __name__=='__main__':main()
