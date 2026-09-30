import json,copy,hashlib,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();dump=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');old=B.parent/'citation-grouping-heldout-v1';case=load(old/'freeze.json')['cases'][1];original=load(old/'runs-glm/case-2/response.json');content=json.loads(original['content']);after=copy.deepcopy(content);added=['ev_cb2cec6acd09b259de55311e','ev_dfcecc92c01e45473eee1e6a','ev_893fdc5c20fa9511a0264aec'];after['parts'][0]['claims'][2]['evidence_ids']+=added
(B/'inputs').mkdir();(B/'inputs/fidelity').mkdir();(B/'.gitignore').write_text('inputs/\nruns-*/\n');response=dict(content=json.dumps(after,ensure_ascii=False),finish_reason='stop',origin='explicit_local_evidence_addition');dump(B/'inputs/response.json',response)
c=query_evidence(FileSourceAdapter(old/'inputs/case-2.txt','qasper:'+case['document_id']),case['source_sha256'],case['question'],[dict(id='P1',question=case['question'])],lambda *_:response,content_budget=60000,prompt_budget=100000,citation_mode='ids',response_language='en',max_unit_bytes=4096);assert c['execution_status']=='complete';dump(B/'inputs/candidate.json',c)
# Evaluate original and derived C3 separately, without revealing treatment or prior verdict.
original_candidate=load(old/'runs-glm/case-2/candidate.json');rows=[]
for cid,candidate in [('a',original_candidate),('b',c)]:
 cl=candidate['parts'][0]['claims'][2];rows.append(dict(id=cid,state=dict(task=case['question'],claims=[dict(id='C3',text=cl['text'],evidence=cl['quotes'])],missing=[])))
dump(B/'inputs/fidelity/cases.json',rows);dump(B/'fidelity-freeze.json',dict(cases_sha256=sha(B/'inputs/fidelity/cases.json'),max_calls=2,expected=dict(a='insufficient',b='supported'),original_candidate_sha256=sha(old/'runs-glm/case-2/candidate.json'),original_response_sha256=sha(old/'runs-glm/case-2/response.json'),derived_candidate_sha256=sha(B/'inputs/candidate.json'),added_ids=added,claim_index=2,claim_text_unchanged=True,reason='Two concrete examples plus the comparison-question reference also needed by the same unchanged claim.',retries=0,timeout_seconds=90,limits='Paired known negative control; producer repair; separate-provider advice, not adjudication. No other candidate text modified.'))
print('Derived valid; quote bytes:',sum(len(q.encode()) for cl in c['parts'][0]['claims'] for q in cl['quotes']))
