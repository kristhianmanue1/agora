"""Offline reconstruction of the frozen two-case experiment; no provider calls."""
import json,hashlib,sys
from pathlib import Path
from types import SimpleNamespace
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.coverage_recovery import build
from agora.rubric_cli import assess
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 f=load(B/'freeze.json');assert sha(B/'run.py')==f['runner_sha256'];rows=[]
 for case in f['cases']:
  out=B/'runs'/case['id'];source=B/'inputs'/f"{case['id']}.txt";rubric=B/f"{case['id']}-rubric.json";candidate=out/'candidate.json';review=out/'review-initial/result.json';proposal=load(out/'proposal.json');c=load(candidate);rv=load(review);j=load(B/'runs-fidelity'/f"{case['id']}-initial.json")
  assert sha(source)==case['source_sha256'] and sha(rubric)==case['rubric_sha256']
  assert rv['candidate_sha256']==sha(candidate)
  assert assess(rv['response'],[r['id'] for r in load(rubric)['requirements']])==rv['requirements']
  args=SimpleNamespace(source=str(source),source_sha256=sha(source),candidate_sha256=sha(candidate),rubric_sha256=sha(rubric),review_sha256=sha(review),part_id='P1',question=case['question'],query=[case['question']],query_origin='Exact original question, frozen before generation',budget=12000,top_k=3,following=3)
  rebuilt=build(source.read_bytes(),candidate.read_bytes(),rubric.read_bytes(),review.read_bytes(),args)
  assert json.loads(json.dumps(rebuilt))=={k:v for k,v in proposal.items() if k!='implementation_sha256'}
  assert proposal['status']=='no_expansion' and not (out/'derived').exists()
  state=json.loads(j['request']['state']);assert state['claims']==[dict(id='C'+str(i),text=cl['text'],evidence=cl['quotes']) for i,cl in enumerate(c['parts'][0]['claims'],1)]
  total=c['response']['usage']['total_tokens']+rv['response']['usage']['total_tokens']+sum(j['response']['usage'][k] for k in ('input_tokens','output_tokens'))
  rows.append(dict(id=case['id'],document_id=case['document_id'],source_bytes=case['source_bytes'],reading_bytes=c['envelope']['delivered_bytes'],candidate_sha256=sha(candidate),review_sha256=sha(review),proposal_sha256=sha(out/'proposal.json'),requirements=rv['requirements'],proposal_status=proposal['status'],fidelity_response=j['response'],http_calls=3,total_reported_tokens=total,claims=c['parts'][0]['claims']))
 return dict(status='completed_not_promoted',rows=rows,http_calls=6,total_reported_tokens=sum(r['total_reported_tokens'] for r in rows),controls=load(B/'controls.json'),unresolved=[dict(case_id=r['id'],claim_id=k) for r in rows for k,v in r['fidelity_response']['answers'].items() if v['choice']!='supported'],scope='Two locally unseen documents; zero live recovery triggers; no estimate of recovery efficacy',total_latency='not_measured',monetary_cost='not_measured',decision='Keep fidelity and coverage separate; do not accept case-2 automatically; preserve original and request adjudication of C6')
if __name__=='__main__':
 report=verify();print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
 if len(sys.argv)==2:
  with Path(sys.argv[1]).open('x') as out:json.dump(report,out,ensure_ascii=False,indent=2);out.write('\n')
