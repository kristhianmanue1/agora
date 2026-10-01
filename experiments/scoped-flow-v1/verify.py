import sys,json
from pathlib import Path
from types import SimpleNamespace
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from verify_common import verify_review,load,sha
from agora.recovery_generation import generate
from agora import scoped_rubric as scoped
f=load(B/'demo-freeze.json');source=R/f['source'];rubric=R/f['rubric'];parent=R/f['candidate'];d=B/'runs/demo';assert sha(parent)==f['candidate_sha256'];assert sha(source)==f['source_sha256'];assert sha(rubric)==f['rubric_sha256']
controls=load(B/'controls-result.json');cf=load(B/'controls-freeze.json')
for c,saved in zip(cf['cases'],controls):
 result=load(B/'runs'/c['id']/'result.json');assert sha(B/'runs'/c['id']/'result.json')==saved['result_sha256'];assert scoped.assess(result['response'],['R1'])==saved['actual'];assert saved['matches']
first=verify_review(source,rubric,parent,f['question'],d/'first',True);assert first['route']['decision']=='expand'
plan=d/'proposal.json';rv=d/'first/coverage/result.json';candidate=d/'second-generation/result.json';args=SimpleNamespace(source=str(source),source_sha256=sha(source),candidate=str(parent),candidate_sha256=sha(parent),rubric=str(rubric),rubric_sha256=sha(rubric),review=str(rv),review_sha256=sha(rv),question=f['question'],part_id='P1',proposal=str(plan),proposal_sha256=sha(plan),response_language='en')
def provider(system,user):assert dict(system=system,user=user)==load(d/'second-generation/request.json');return load(d/'second-generation/response.json')
replay=generate(args,provider);assert replay['parts']==load(candidate)['parts'];second=verify_review(source,rubric,candidate,f['question'],d/'second');assert second['route']['decision']=='candidate_ready_for_explicit_review'
p=load(plan);assert all(any(a<=x and y<=b for a,b in p['ranges']) for x,y in p['initial_ranges'])
gen=load(candidate);report=dict(status='transition_demonstrated',controls=controls,first=first,second=second,initial_bytes=p['initial_bytes'],expanded_bytes=p['delivered_bytes'],candidate_sha256=sha(candidate),original_unchanged=True,replay_verified=True,http_calls=10,total_reported_tokens=sum(x['response']['usage']['total_tokens'] for x in controls)+first['tokens']+second['tokens']+gen['response']['usage']['total_tokens'],memory_admission='not_performed')
if len(sys.argv)>1:
 with Path(sys.argv[1]).open('x') as out:json.dump(report,out,indent=2);out.write('\n')
print({k:v for k,v in report.items() if k not in ('controls','first','second')})
