import json,sys,hashlib,time
from pathlib import Path
from types import SimpleNamespace
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.issue_cli import main
from agora.source import FileSourceAdapter
from agora.subquestions import prepare_subquestions
from agora.evidence import query_evidence
from agora.plan_generation import live_provider
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
f=load(B/'freeze.json');assert sha(Path(__file__))==f['runner_sha256']
root=B/'runs';root.mkdir(exist_ok=False);cli=['--workspace',str(B/'inputs/workspace')];assert main(cli+['init'])==0
for case in f['cases']:
 cid=case['id'];out=root/cid;out.mkdir();source=B/'inputs'/f'{cid}.txt';rubric=B/f'{cid}-rubric.json';assert sha(source)==case['source_sha256'] and sha(rubric)==case['rubric_sha256']
 adapter=FileSourceAdapter(source,'qasper:'+case['document_id']);plan=prepare_subquestions(adapter,case['source_sha256'],dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='P1',query=case['question'],reference_ranges=[])]),8000,4)
 dump(out/'initial-plan.json',plan);calls=0
 def provider(system,user):
  global calls
  assert calls==0;calls+=1;dump(out/'request.json',dict(system=system,user=user));dump(out/'receipt.json',dict(status='attempted',http_calls=1));start=time.monotonic()
  try:
   response=live_provider(system,user,max_tokens=4096,json_object=True);dump(out/'response.json',response);dump(out/'receipt.json',dict(status='returned',http_calls=1,elapsed_seconds=time.monotonic()-start));return response
  except Exception as exc:
   dump(out/'receipt.json',dict(status='failed',error=type(exc).__name__,http_calls=1));raise
 candidate=query_evidence(adapter,case['source_sha256'],case['question'],[dict(id='P1',question=case['question'])],provider,ranges=[(s['start_byte'],s['end_byte']) for s in plan['envelope']['spans']],content_budget=8000,prompt_budget=100000,citation_mode='ids',response_language='en',max_unit_bytes=4096)
 dump(out/'candidate.json',candidate);print(cid,'initial',candidate['execution_status'],flush=True)
 if candidate['execution_status']!='complete':continue
 common=['--source',str(source),'--source-sha256',sha(source),'--rubric',str(rubric),'--rubric-sha256',sha(rubric),'--part-id','P1','--question',case['question']]
 parent=['--candidate',str(out/'candidate.json'),'--candidate-sha256',sha(out/'candidate.json')]
 if main(cli+['review-rubric']+common+parent+['--live','--out',str(out/'review-initial')]):continue
 review=out/'review-initial/result.json';review_args=['--review',str(review),'--review-sha256',sha(review)]
 proposal=out/'proposal.json'
 if main(cli+['coverage-plan']+common+parent+review_args+['--query',case['question'],'--query-origin','Exact original question, frozen before generation','--budget','12000','--top-k','3','--following','3','--out',str(proposal)]):continue
 if load(proposal)['status']!='proposed':continue
 if main(cli+['generate-recovery']+common+parent+review_args+['--proposal',str(proposal),'--proposal-sha256',sha(proposal),'--response-language','en','--live','--out',str(out/'derived')]):continue
 derived=out/'derived/result.json'
 main(cli+['review-rubric']+common+['--candidate',str(derived),'--candidate-sha256',sha(derived),'--live','--out',str(out/'review-derived')])
