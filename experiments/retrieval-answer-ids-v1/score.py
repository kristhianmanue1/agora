import json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;old=B.parent/'retrieval-answer-paired-v1'
load=lambda p:json.loads(p.read_text())
f=load(B/'freeze.json');assert hashlib.sha256((B/'inputs/cases.json').read_bytes()).hexdigest()==f['cases_sha256']
inputs={x['id']:x for x in load(B/'inputs/cases.json')};v={x['id']:x for x in load(B/'validation.json')};reviewinputs={x['id']:x for x in load(B/'inputs/review-02/cases.json')};records=[]
for c in load(B/'key.json'):
 cid=c['id'];p=B/'runs-generation'/f'{cid}.json';g=load(p) if p.exists() else dict(status='not_run',elapsed_seconds=0)
 if p.exists():assert g['request']['messages']==[dict(role='system',content=inputs[cid]['system']),dict(role='user',content=inputs[cid]['user'])]
 ep=old/'inputs'/f"{c['previous_id']}-envelope.json";assert hashlib.sha256(ep.read_bytes()).hexdigest()==f['envelope_sha256'][c['previous_id']]
 usage=g.get('response',{}).get('usage',{});gen=dict(status=g['status'],**{k:v[cid].get(k) for k in ('valid','answer_status','diagnostics','reference_count')},input_tokens=usage.get('prompt_tokens'),output_tokens=usage.get('completion_tokens'),elapsed_seconds=g.get('elapsed_seconds'),model=g.get('response',{}).get('model'));review=None
 q=B/'runs-review'/f'{cid}.json'
 if q.exists():
  rev=load(q);assert json.loads(rev['request']['state'])=={k:reviewinputs[cid][k] for k in ('task','evidence','answer')};raw=rev.get('response',{});u=raw.get('usage',{});review=dict(status=rev['status'],labels={k:x['choice'] for k,x in raw.get('answers',{}).items()},input_tokens=u.get('input_tokens'),output_tokens=u.get('output_tokens'),elapsed_seconds=rev.get('elapsed_seconds'),model=raw.get('model'))
 usable=bool(gen['valid'] and gen['answer_status']=='answered' and review['labels']==dict(fidelity='supported',coverage='complete')) if review and review['status']=='completed' else None
 records.append(dict(c,generation=gen,review=review,usable_by_reviewer=usable))
summary={}
for method in ('equal','shared'):
 rr=[x for x in records if x['method']==method];s=dict(planned=len(rr),attempted=sum(x['generation']['status']!='not_run' for x in rr),transport_failed=sum(x['generation']['status']=='failed' for x in rr),valid=sum(x['generation']['valid'] for x in rr),rejected=sum(x['generation']['status']=='completed' and not x['generation']['valid'] for x in rr),reviewed=sum(bool(x['review'] and x['review']['status']=='completed') for x in rr),usable=sum(x['usable_by_reviewer'] is True for x in rr))
 s['answer_statuses']={status:sum(x['generation']['answer_status']==status for x in rr) for status in ('answered','partial','not_in_passages')}
 for axis in ('generation','review'):
  for metric in ('input_tokens','output_tokens','elapsed_seconds'):s[axis+'_'+metric]=round(sum((x[axis] or {}).get(metric) or 0 for x in rr),3)
 s['known_tokens']=sum(s[a+'_'+m] for a in ('generation','review') for m in ('input_tokens','output_tokens'));summary[method]=s
pairs=[]
for oldpair in load(old/'result-resumed.json')['pairs']:
 rr={x['method']:x for x in records if x['document_id']==oldpair['document_id']};a=rr['equal']['usable_by_reviewer'];b=rr['shared']['usable_by_reviewer'];outcome='incomplete_pair' if a is None or b is None else 'shared_win' if b and not a else 'equal_win' if a and not b else 'both_usable' if a else 'neither_usable';pairs.append(dict(document_id=oldpair['document_id'],same_context=oldpair['same_context'],outcome=outcome,previous_outcome=oldpair['outcome']))
result=dict(summary=summary,pairs=pairs,records=records,known_tokens=sum(s['known_tokens'] for s in summary.values()),limitations=f['limitations']);(B/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary));print(json.dumps(pairs));print('tokens',result['known_tokens'])
