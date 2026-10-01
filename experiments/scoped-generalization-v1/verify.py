import sys,json
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path[:0]=[str(R/'src'),str(R/'experiments/scoped-flow-v1')]
from verify_common import verify_review,load,sha
from agora.plan_generation import generate
f=load(B/'fixed-freeze.json');assert sha(B/'run_fixed.py')==f['runner_sha256'];assert sha(R/'src/agora/plan_generation.py')==f['plan_generation_sha256'];rows=[];tokens=0;calls=0
for c in f['cases']:
 out=B/'runs-fixed'/c['id'];source=R/c['source_path'];rubric=R/c['rubric_path'];candidate=out/'generation/result.json';plan=out/'plan.json';saved=load(candidate)
 original=load(B/'runs'/c['id']/'generation/result.json');assert original['http_attempts']==0 and original['execution_status']=='rejected'
 def provider(system,user):assert saved['prompt']==dict(system=system,user=user);return saved['response']
 replay=generate(source,plan.read_bytes(),sha(plan),c['question'],provider,'ids');assert replay['parts']==saved['parts'];assert replay['envelope']==saved['envelope']
 r=verify_review(source,rubric,candidate,c['question'],out);row=dict(id=c['id'],format=c['format'],candidate_sha256=sha(candidate),generation_response=saved['response'],parts=saved['parts'],reading_bytes=saved['envelope']['delivered_bytes'],**r);row['http_calls']+=saved['http_attempts'];row['tokens']+=saved['response']['usage']['total_tokens'];tokens+=row['tokens'];calls+=row['http_calls'];rows.append(row)
assert calls<=f['max_http_calls'];report=dict(status='complete_mixed_outcomes',rows=rows,http_calls=calls,total_reported_tokens=tokens,replay_verified=True,initial_cli_defect_attempts=4,initial_cli_defect_http_calls=0,monetary_cost='not_measured',scope=f['scope'])
if len(sys.argv)>1:
 with Path(sys.argv[1]).open('x') as out:json.dump(report,out,ensure_ascii=False,indent=2);out.write('\n')
for r in rows:print(r['id'],r['route']['decision'],r['requirements'],r['fidelity'],r['tokens'])
print(calls,tokens)
