"""Verify source diagnosis, preserved inputs and replay; no network calls."""
import hashlib,json,sys
from pathlib import Path
from types import SimpleNamespace
B=Path(__file__).resolve().parent;R=B.parents[1];P=R/'experiments/scoped-generalization-v1'
sys.path[:0]=[str(R/'src'),str(R/'experiments/scoped-flow-v1')]
from verify_common import verify_review
from agora.recovery_generation import generate
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=load(B/'freeze.json');assert sha(B/'run.py')==f['runner_sha256']
for p,h in f['bindings'].items():assert sha(R/p)==h,p
out=B/'runs';source=P/'inputs/case-2.txt';rubric=P/'case-2-rubric.json';parent=P/'runs-fixed/case-2/generation/result.json';rv=P/'runs-fixed/case-2/coverage/result.json';plan=out/'proposal.json';candidate=out/'generation/result.json'
a=SimpleNamespace(source=str(source),source_sha256=sha(source),candidate=str(parent),candidate_sha256=sha(parent),rubric=str(rubric),rubric_sha256=sha(rubric),review=str(rv),review_sha256=sha(rv),part_id='P1',question=f['question'],proposal=str(plan),proposal_sha256=sha(plan),response_language='es')
saved=load(candidate)
def provider(system,user):
 assert load(out/'generation/request.json')==dict(system=system,user=user)
 return load(out/'generation/response.json')
replay=generate(a,provider);assert replay['parts']==saved['parts'];assert replay['envelope']==saved['envelope']
r=verify_review(source,rubric,candidate,f['question'],out)
p=load(plan);old=load(parent);assert all(any(c<=x['start_byte'] and x['end_byte']<=d for c,d in p['ranges']) for x in old['envelope']['spans'])
annotations=load(P/'inputs/case-2-annotations.json');assert len(annotations)==2
external=[]
for x in annotations:
 answer=x['answer'];assert all(t in source.read_text() for t in answer['evidence'])
 external.append(dict(annotation_id=x['annotation_id'],answer=answer['free_form_answer'] or answer['extractive_spans'],evidence_matches_source=True))
refs=[]
for x in load(rubric)['requirements']:
 e=x['evidence'];assert source.read_bytes()[e['start_byte']:e['end_byte']].decode()==e['text']
 refs.append(dict(id=x['id'],in_expanded_context=any(c<=e['start_byte'] and e['end_byte']<=d for c,d in p['ranges'])))
js=P/'inputs/jsonl.jsonl';lines=[json.loads(x) for x in js.read_text().splitlines()];assert len(lines)==2
assert lines[0]['text']=='Draft date: Tuesday.' and lines[1]['text']=='Correction: Wednesday; Tuesday is cancelled.'
jcandidate=load(P/'runs-fixed/jsonl/generation/result.json');jf=load(P/'runs-fixed/jsonl/fidelity/result.json')
assert jf['response']['answers']['P1_0']['choice']=='supported' and jf['response']['answers']['P1_1']['choice']=='supported' and jf['response']['answers']['missing']['choice']=='insufficient'
report=dict(schema=f['schema'],scope=f['scope'],replay_verified=True,qasper=dict(source_sha256=sha(source),external_annotations=external,annotation_limit='Pre-existing human annotations; original rubric used first annotation. No blind new adjudication.',initial_bytes=p['initial_bytes'],expanded_bytes=p['delivered_bytes'],reference_presence=refs,visual7w_in_initial=any('Visual7W' in x['text'] for x in old['envelope']['spans']),visual7w_in_expanded=any('Visual7W' in x['text'] for x in p['envelope']['spans']),parts=saved['parts'],generation_response=saved['response'],**r),jsonl=dict(source_sha256=sha(js),source_records=lines,original_missing= jcandidate['parts'][0]['missing'],original_route='requires_fidelity_inspection',observed_labels={k:v['choice'] for k,v in jf['response']['answers'].items()},technical_assessment='Wednesday supersedes Tuesday within the observed record. Lack of later records is a scope limitation, not proof that later changes did or did not occur.',recommended_answer='Según el registro disponible hasta las 09:15, la fecha es miércoles; sustituye al martes, que fue cancelado.',assessment_status='Same-session source inspection, not independent adjudication; original artifacts and route unchanged',http_calls=0),memory_admission='not_performed')
report['http_calls']=saved['http_attempts']+r['http_calls'];report['total_reported_tokens']=saved['response']['usage']['total_tokens']+r['tokens'];assert report['http_calls']<=f['max_http_calls']
if len(sys.argv)>1:
 with Path(sys.argv[1]).open('x') as h:json.dump(report,h,ensure_ascii=False,indent=2);h.write('\n')
print(json.dumps(dict(replay_verified=True,http_calls=report['http_calls'],tokens=report['total_reported_tokens'],decision=r['route']['decision'],requirements=r['requirements'],references=refs),ensure_ascii=False))
