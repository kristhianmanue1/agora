import sys,json,time,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter
from agora.plan_generation import live_provider
from agora.issue_cli import main
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
f=load(B/'live-freeze.json');assert sha(Path(__file__))==f['runner_sha256'];root=B/'runs-glm';root.mkdir(exist_ok=False);cli=['--workspace',str(B/'inputs/workspace')];assert main(cli+['init'])==0
for c in f['cases']:
 out=root/c['id'];out.mkdir();source=R/c['source_path'];rubric=R/c['rubric_path'];assert sha(source)==c['source_sha256'] and sha(rubric)==c['rubric_sha256'];attempts=0
 def provider(system,user):
  global attempts
  assert attempts==0;attempts+=1;dump(out/'request.json',dict(system=system,user=user));dump(out/'receipt.json',dict(status='attempted',http_calls=1));start=time.monotonic()
  try:
   response=live_provider(system,user,max_tokens=4096,json_object=True);dump(out/'response.json',response);dump(out/'receipt.json',dict(status='returned',http_calls=1,elapsed_seconds=time.monotonic()-start));return response
  except Exception as exc:
   dump(out/'receipt.json',dict(status='failed',http_calls=1,error=type(exc).__name__,elapsed_seconds=time.monotonic()-start));raise
 candidate=query_evidence(FileSourceAdapter(source,c['document_id']),c['source_sha256'],c['question'],[dict(id='P1',question=c['question'])],provider,ranges=c['ranges'],content_budget=c['budget'],prompt_budget=100000,citation_mode='ids',response_language='en',max_unit_bytes=4096);dump(out/'candidate.json',candidate);print(c['id'],candidate['execution_status'],flush=True)
 if candidate['execution_status']!='complete':continue
 start=time.monotonic();code=main(cli+['review-rubric','--source',str(source),'--source-sha256',c['source_sha256'],'--candidate',str(out/'candidate.json'),'--candidate-sha256',sha(out/'candidate.json'),'--rubric',str(rubric),'--rubric-sha256',c['rubric_sha256'],'--part-id','P1','--question',c['question'],'--live','--out',str(out/'review')]);dump(out/'review-receipt.json',dict(exit_code=code,elapsed_seconds=time.monotonic()-start))
