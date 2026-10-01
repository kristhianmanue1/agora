"""Verify replay and count observed costs, including failed attempts."""
import json,hashlib,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def score():
 f=load(B/'live-freeze.json');assert sha(B/'live.py')==f['runner_sha256'];rows=[]
 for case in f['cases']:
  out=B/'runs-glm'/case['id'];c=load(out/'candidate.json');source=R/case['source_path'];assert sha(source)==case['source_sha256'];receipt=load(out/'receipt.json');response=load(out/'response.json') if (out/'response.json').exists() else None
  if response:
   request=load(out/'request.json')
   def provider(system,user):assert dict(system=system,user=user)==request;return response
   replay=query_evidence(FileSourceAdapter(source,case['document_id']),case['source_sha256'],case['question'],[dict(id='P1',question=case['question'])],provider,ranges=case['ranges'],content_budget=case['budget'],prompt_budget=100000,citation_mode='ids',response_language='en',max_unit_bytes=4096)
   for key in ('parts','envelope','execution_status','diagnostics'):assert replay.get(key)==c.get(key)
  review=load(out/'review/result.json') if (out/'review/result.json').exists() else None;jpath=B/'runs-fidelity'/f"{case['id']}.json";j=load(jpath) if jpath.exists() else None
  if review:assert review['candidate_sha256']==sha(out/'candidate.json')
  if j:
   state=json.loads(j['request']['state']);assert state['claims']==[dict(id='C'+str(i),text=cl['text'],evidence=cl['quotes']) for i,cl in enumerate(c['parts'][0]['claims'],1)]
  tokens=(response or {}).get('usage',{}).get('total_tokens',0)+(review or {}).get('response',{}).get('usage',{}).get('total_tokens',0)
  if j:tokens+=sum(j.get('response',{}).get('usage',{}).get(k,0) for k in ('input_tokens','output_tokens'))
  seconds=receipt.get('elapsed_seconds',0)+(load(out/'review-receipt.json')['elapsed_seconds'] if review else 0)+(j or {}).get('elapsed_seconds',0)
  rows.append(dict(id=case['id'],budget=case['budget'],reading_bytes=case['reading_bytes'],generation_status=c['execution_status'],generation_diagnostics=c.get('diagnostics'),coverage_status=(review or {}).get('status','not_run'),requirements=(review or {}).get('requirements'),fidelity_status=(j or {}).get('status','not_run'),fidelity_answers=(j or {}).get('response',{}).get('answers'),generation_usage=(response or {}).get('usage'),total_reported_tokens=tokens,elapsed_seconds=round(seconds,3),http_calls=receipt['http_calls']+(review or {}).get('http_attempts',0)+(1 if j else 0),candidate_sha256=sha(out/'candidate.json'),parts=c.get('parts'),generation_response=response,coverage_response=(review or {}).get('response'),fidelity_response=(j or {}).get('response')))
 calls=sum(r['http_calls'] for r in rows);assert calls<=f['max_calls']
 return dict(status='complete_not_promoted',rows=rows,aliases=f['aliases'],http_calls=calls,total_reported_tokens=sum(r['total_reported_tokens'] for r in rows),elapsed_seconds=round(sum(r['elapsed_seconds'] for r in rows),3),monetary_cost='not_measured',scope='Known cases, one draw per distinct context; no statistical optimum; coverage rubric incomplete for case 1',replay_verified=True)
if __name__=='__main__':
 r=score()
 if len(sys.argv)>1:
  with Path(sys.argv[1]).open('x') as out:json.dump(r,out,ensure_ascii=False,indent=2);out.write('\n')
 for x in r['rows']:print(x['id'],x['generation_status'],x['coverage_status'],x['requirements'],x['total_reported_tokens'],x['fidelity_status'])
 print({k:v for k,v in r.items() if k not in ('rows','aliases')})
