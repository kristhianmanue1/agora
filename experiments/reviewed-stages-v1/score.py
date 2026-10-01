import json,sys,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from policy import decide
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def score():
 f=load(B/'freeze.json')
 for p,h in f['implementations'].items():assert sha(R/p)==h
 rows=[];calls=0;tokens=0
 for case in f['cases']:
  previous=[];last=None
  for i,stage in enumerate(case['stages']):
   out=B/'runs'/case['id']/str(i)
   if not out.exists():break
   assert last is None or last=='expand'
   candidate=load(out/'candidate.json');response=load(out/'response.json') if (out/'response.json').exists() else None;receipt=load(out/'receipt.json');source=R/case['source_path'];assert sha(source)==case['source_sha256'];assert sha(R/case['rubric_path'])==case['rubric_sha256']
   if response:
    request=load(out/'request.json')
    def provider(system,user):assert dict(system=system,user=user)==request;return response
    replay=query_evidence(FileSourceAdapter(source,case['document_id']),case['source_sha256'],case['question'],[dict(id='P1',question=case['question'])],provider,ranges=stage['ranges'],content_budget=stage['budget'],prompt_budget=100000,citation_mode='ids',response_language='en',max_unit_bytes=4096)
    for key in ('parts','envelope','execution_status','diagnostics'):assert replay.get(key)==candidate.get(key)
   coverage=load(out/'review/result.json') if (out/'review/result.json').exists() else {};fidelity=load(out/'fidelity/candidate.json') if (out/'fidelity/candidate.json').exists() else {}
   if coverage:assert coverage['candidate_sha256']==sha(out/'candidate.json')
   if fidelity:
    state=json.loads(fidelity['request']['state']);assert state['claims']==[dict(id='C'+str(i),text=c['text'],evidence=c['quotes']) for i,c in enumerate(candidate['parts'][0]['claims'],1)]
   assert all(any(a<=x and y<=b for a,b in stage['ranges']) for x,y in previous);previous=stage['ranges']
   decision=load(out/'decision.json');assert decision['candidate_sha256']==sha(out/'candidate.json');assert decision['decision']==decide(candidate['execution_status'],coverage,fidelity,i+1<len(case['stages']));last=decision['decision']
   n=receipt['http_calls']+coverage.get('http_attempts',0)+(1 if fidelity else 0);usage=(response or {}).get('usage',{}).get('total_tokens',0)+coverage.get('response',{}).get('usage',{}).get('total_tokens',0)+sum(fidelity.get('response',{}).get('usage',{}).get(k,0) for k in ('input_tokens','output_tokens'));calls+=n;tokens+=usage
   rows.append(dict(case_id=case['id'],document_id=case['document_id'],stage=i,budget=stage['budget'],reading_bytes=stage['bytes'],decision=decision,http_calls=n,total_reported_tokens=usage,generation_status=candidate['execution_status'],parts=candidate.get('parts'),coverage_status=coverage.get('status'),requirements=coverage.get('requirements'),coverage_response=coverage.get('response'),fidelity_response=fidelity.get('response'),generation_response=response,candidate_sha256=sha(out/'candidate.json')))
  assert last is not None and last!='expand'
 assert calls<=f['max_calls']
 return dict(status='complete_not_promoted',rows=rows,http_calls=calls,total_reported_tokens=tokens,monetary_cost='not_measured',replay_verified=True,memory_admission='not_performed',scope='Experimental review routing on three cases, not product integration or independent adjudication')
if __name__=='__main__':
 r=score()
 if len(sys.argv)>1:
  with Path(sys.argv[1]).open('x') as out:json.dump(r,out,ensure_ascii=False,indent=2);out.write('\n')
 for x in r['rows']:print(x['case_id'],x['budget'],x['decision']['decision'],x['requirements'],x['total_reported_tokens'])
 print({k:v for k,v in r.items() if k!='rows'})
