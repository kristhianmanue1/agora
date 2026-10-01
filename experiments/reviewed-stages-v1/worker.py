import json,hashlib,sys,time,importlib.util
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
f=load(B/'freeze.json');case=next(c for c in f['cases'] if c['id']==sys.argv[2]);step=int(sys.argv[3]);out=B/'runs'/case['id']/str(step);stage=case['stages'][step]
if sys.argv[1]=='glm':
 from agora.evidence import query_evidence
 from agora.source import FileSourceAdapter
 from agora.plan_generation import live_provider
 from agora.issue_cli import main
 out.mkdir();source=R/case['source_path'];rubric=R/case['rubric_path'];assert sha(source)==case['source_sha256'] and sha(rubric)==case['rubric_sha256'];attempts=0
 def provider(system,user):
  global attempts
  assert attempts==0;attempts+=1;dump(out/'request.json',dict(system=system,user=user));dump(out/'receipt.json',dict(status='attempted',http_calls=1));start=time.monotonic()
  try:
   response=live_provider(system,user,max_tokens=4096,json_object=True);dump(out/'response.json',response);dump(out/'receipt.json',dict(status='returned',http_calls=1,elapsed_seconds=time.monotonic()-start));return response
  except Exception as exc:
   dump(out/'receipt.json',dict(status='failed',http_calls=1,error=type(exc).__name__,elapsed_seconds=time.monotonic()-start));raise
 candidate=query_evidence(FileSourceAdapter(source,case['document_id']),case['source_sha256'],case['question'],[dict(id='P1',question=case['question'])],provider,ranges=stage['ranges'],content_budget=stage['budget'],prompt_budget=100000,citation_mode='ids',response_language='en',max_unit_bytes=4096);dump(out/'candidate.json',candidate)
 if candidate['execution_status']=='complete':
  main(['--workspace',str(B/'inputs/workspace'),'review-rubric','--source',str(source),'--source-sha256',case['source_sha256'],'--candidate',str(out/'candidate.json'),'--candidate-sha256',sha(out/'candidate.json'),'--rubric',str(rubric),'--rubric-sha256',case['rubric_sha256'],'--part-id','P1','--question',case['question'],'--live','--out',str(out/'review')])
elif sys.argv[1]=='jev':
 def module(name,path):
  s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 criteria=module('criteria',R/'experiments/reading-paired-grouping-v1/run_jev.py');transport=module('transport',R/'experiments/reviewer-comparison-v1/run.py')
 candidate=load(out/'candidate.json');part=candidate['parts'][0];state=dict(task=case['question'],claims=[dict(id='C'+str(i),text=c['text'],evidence=c['quotes']) for i,c in enumerate(part['claims'],1)],missing=part['missing'])
 if part['missing']:state['full_source_for_missing_only']='\n\n'.join(s['text'] for s in candidate['envelope']['spans'])
 assert len(json.dumps(state).encode())<=65536
 (out/'fidelity-input').mkdir();dump(out/'fidelity-input/cases.json',[dict(id='candidate',state=state,candidate_sha256=sha(out/'candidate.json'))]);transport.BASE=out/'fidelity-input';transport.payload=criteria.payload;transport.label=criteria.label;sys.argv=['transport','jev','--out',str(out/'fidelity')];transport.main()
else:raise ValueError('mode')
