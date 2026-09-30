import json,hashlib,sys,importlib.util,time,subprocess,random
from pathlib import Path
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'src'))
from agora.qasper import render
from agora.source import FileSourceAdapter
from agora.subquestions import prepare_subquestions
from agora.routed_query import response_system,prompt
p=r/'experiments/shared-neighbor-validation-v1';s=importlib.util.spec_from_file_location('validation',p/'validate.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
b=r/'experiments/retrieval-answer-paired-v1';b.mkdir();(b/'inputs').mkdir();protocol=json.loads((p/'protocol.json').read_text());raw=(r/'experiments/qasper-v1/inputs/test.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==protocol['dataset_sha256'];dataset=json.loads(raw)
cases=[];key=[];reports=[];sources={}
for i,item in enumerate(protocol['selected']):
 pid=item['document_id'];paper=dataset[pid];data,_=render(paper);revision=hashlib.sha256(data).hexdigest();source=b/'inputs'/f'{pid}.txt';source.write_bytes(data);sources[pid]=revision
 qa=next(q for q in paper['qas'] if q['question_id']==item['question_id']);question=qa['question'];sp=m.spec([question,'Which methods, data, conditions and results support the answer to: '+question]);adapter=FileSourceAdapter(source,'qasper:'+pid)
 start=time.monotonic();plan=prepare_subquestions(adapter,revision,sp,budget=8000,top_k=3);base_seconds=time.monotonic()-start;start=time.monotonic();ranges=m.expand(data,plan,sp,8000);shared=adapter.fetch(revision,[tuple(x) for x in ranges],content_budget=8000) if ranges else None;extra_seconds=time.monotonic()-start
 for method in (['equal','shared'] if i%2==0 else ['shared','equal']):
  env=plan['envelope'] if method=='equal' else shared;cid='x'+hashlib.sha256((pid+':'+method+':paired-v1').encode()).hexdigest()[:10]
  if not env:raise RuntimeError('empty_retrieval_case_requires_record')
  u,size=prompt(question,[dict(id='P1',question=question)],env,'en','concise-v1');assert size<=65536
  cases.append(dict(id=cid,system=response_system('en','concise-v1'),user=u))
  key.append(dict(id=cid,document_id=pid,question_id=item['question_id'],method=method,question=question,delivered_bytes=env['delivered_bytes'],retrieval_seconds=base_seconds+(extra_seconds if method=='shared' else 0)))
  (b/'inputs'/f'{cid}-envelope.json').write_text(json.dumps(env,ensure_ascii=False,indent=2)+'\n')
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
dump(b/'inputs/cases.json',cases);dump(b/'key.json',key)
dump(b/'freeze.json',dict(code_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),cases_sha256=hashlib.sha256((b/'inputs/cases.json').read_bytes()).hexdigest(),sources=sources,documents=12,max_generation_calls=24,max_review_calls=24,timeout_seconds=90,retries=0,generator='glm-5.3-flash',reviewer='jev-1.13.0',generation_output_tokens=2048,profile='existing concise-v1 in English; literal citations',budgets=8000,temperature=0,order='alternate method first by document; neutral hashed ids; shuffle review order seed paired-review-v1',primary='Compare valid answers with supported claims and no task omissions; include invalid outputs and unnecessary abstentions as failures; report paired wins/losses and total tokens by route; no promotion by majority alone',limits='12 development documents previously used for coverage; one draw per method; Jev reviewer uncalibrated, no human adjudication; review uses full source and excludes gold/method'))
(b/'.gitignore').write_text('inputs/\nruns-*/\n')
print('Prepared',len(cases),'generation cases')
