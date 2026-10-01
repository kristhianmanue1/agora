"""Recheck locally retained live artifacts without another provider call."""
import json,hashlib,sys
from pathlib import Path
from types import SimpleNamespace
B=Path(__file__).resolve().parent;ROOT=B.parents[1];sys.path.insert(0,str(ROOT/'src'))
from agora.recovery_generation import generate
from agora.rubric_cli import assess
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 base=B.parent/'condition-expansion-heldout-v1';freeze=load(B/'freeze.json')
 files=dict(source=base/'inputs/expanded.txt',candidate=base/'runs-glm/expanded/candidate.json',rubric=base/'expanded-rubric.json',review=base/'runs-review-expanded/result.json')
 assert freeze['inputs']=={k:sha(p) for k,p in files.items()}
 kw=dict(proposal=str(B/'inputs/proposal.json'),proposal_sha256=freeze['proposal_sha256'],part_id='P1',question='What metrics are used to measure bias reduction?',response_language='en')
 for k,p in files.items():kw[k]=str(p);kw[k+'_sha256']=sha(p)
 candidate=load(B/'runs-generation/result.json');request=load(B/'runs-generation/request.json');response=load(B/'runs-generation/response.json');calls=[]
 def provider(system,user):
  assert dict(system=system,user=user)==request;calls.append(1);return response
 replay=generate(SimpleNamespace(**kw),provider)
 assert len(calls)==1 and replay['execution_status']=='complete'
 for k in ('parts','envelope','parent_candidate_sha256','parent_review_sha256','recovery_proposal_sha256'):assert replay[k]==candidate[k]
 review=load(B/'runs-review/result.json');assert review['candidate_sha256']==sha(B/'runs-generation/result.json')
 assert assess(review['response'],['R1','R2','R3','R4'])==review['requirements']
 fidelity=load(B/'runs-jev/recovered.json');cases=load(B/'inputs/fidelity/cases.json');assert cases[0]['candidate_sha256']==sha(B/'runs-generation/result.json')
 assert json.loads(fidelity['request']['state'])==cases[0]['state']
 assert {a['choice'] for a in fidelity['response']['answers'].values()}=={'supported'}
 totals=response['usage']['total_tokens']+review['response']['usage']['total_tokens']+sum(fidelity['response']['usage'][k] for k in ('input_tokens','output_tokens'))
 return dict(status='pass',scope='known regression, not held-out validation',candidate_sha256=sha(B/'runs-generation/result.json'),review_sha256=sha(B/'runs-review/result.json'),fidelity_sha256=sha(B/'runs-jev/recovered.json'),context_bytes=candidate['envelope']['delivered_bytes'],requirements=review['requirements'],fidelity=fidelity['response'],http_calls=3,total_reported_tokens=totals,original_inputs_unchanged=True,replay_verified=True,latency_total='not_measured',monetary_cost='not_measured')
if __name__=='__main__':
 result=verify();print(json.dumps({k:v for k,v in result.items() if k!='fidelity'},indent=2))
 if len(sys.argv)==2:
  with Path(sys.argv[1]).open('x') as out:json.dump(result,out,indent=2);out.write('\n')
