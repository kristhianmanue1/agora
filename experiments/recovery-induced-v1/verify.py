"""Offline replay, including failed outcomes; never call a provider."""
import json,hashlib,sys
from pathlib import Path
from types import SimpleNamespace
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.recovery_generation import generate
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 f=load(B/'freeze.json');assert sha(B/'run.py')==f['runner_sha256'];assert all(sha(R/'src/agora'/n)==h for n,h in f['implementation_hashes'].items());rows=[];tokens=0;calls=0
 for case in f['cases']:
  cid=case['id'];out=B/'runs'/cid;source=B/'inputs'/f'{cid}.txt';rubric=B/f'{cid}-rubric.json';parent=out/'candidate.json';review=out/'review-initial/result.json';proposal=out/'proposal.json';derived=out/'derived/result.json'
  assert sha(source)==case['source_sha256'] and sha(rubric)==case['rubric_sha256'];assert sha(parent)==case['seed_sha256']
  args=SimpleNamespace(source=str(source),source_sha256=sha(source),candidate=str(parent),candidate_sha256=sha(parent),rubric=str(rubric),rubric_sha256=sha(rubric),review=str(review),review_sha256=sha(review),part_id='P1',question=case['question'],proposal=str(proposal),proposal_sha256=sha(proposal),response_language='en')
  response=load(out/'derived/response.json');request=load(out/'derived/request.json')
  def provider(system,user):assert dict(system=system,user=user)==request;return response
  result=generate(args,provider);saved=load(derived);assert result['execution_status']==saved['execution_status'];assert result.get('parts')==saved.get('parts');assert result.get('diagnostics')==saved.get('diagnostics')
  plan=load(proposal);ranges=plan['ranges'];evidence={r['id']:any(a<=r['evidence']['start_byte'] and r['evidence']['end_byte']<=b for a,b in ranges) for r in load(rubric)['requirements']}
  artifacts=[review,derived];after=out/'review-derived/result.json'
  if after.exists():artifacts.append(after)
  for path in artifacts:
   v=load(path);calls+=v['http_attempts'];tokens+=v.get('response',{}).get('usage',{}).get('total_tokens',0)
  fidelity=B/'runs-fidelity'/f'{cid}-derived.json';j=load(fidelity) if fidelity.exists() else None
  if j:
   calls+=1;tokens+=sum(j['response']['usage'][k] for k in ('input_tokens','output_tokens'))
   state=json.loads(j['request']['state']);assert state['claims']==[dict(id='C'+str(i),text=cl['text'],evidence=cl['quotes']) for i,cl in enumerate(saved['parts'][0]['claims'],1)]
  rows.append(dict(id=cid,document_id=case['document_id'],initial_bytes=case['initial_bytes'],reading_bytes=plan['delivered_bytes'],generation_status=saved['execution_status'],diagnostics=saved.get('diagnostics'),rubric_evidence_in_context=evidence,coverage_review=load(after) if after.exists() else None,fidelity_response=j['response'] if j else None,candidate_sha256=sha(derived),response_sha256=sha(out/'derived/response.json'),parts=saved.get('parts'),generation_response=response,initial_review_sha256=sha(review),proposal_sha256=sha(proposal)))
 assert calls<=f['max_http_calls']
 return dict(status='completed_no_end_to_end_success',scope=f['scope'],rows=rows,http_calls=calls,total_reported_tokens=tokens,retries=0,replay_verified=True,decision='No promotion; preserve format rejection and incomplete coverage review. Design a separate condition before any retry or changed budget.')
if __name__=='__main__':
 r=verify();print(json.dumps({k:v for k,v in r.items() if k!='rows'},indent=2));print([(x['id'],x['rubric_evidence_in_context']) for x in r['rows']])
 if len(sys.argv)==2:
  with Path(sys.argv[1]).open('x') as out:json.dump(r,out,ensure_ascii=False,indent=2);out.write('\n')
