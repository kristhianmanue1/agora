import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=R/'experiments/retrieval-answer-paired-v1';old=json.loads((B/'result.json').read_text());rows=old['records'];continuation=json.loads((B/'continuation-01.json').read_text());inputs={x['id']:x for x in json.loads((B/'inputs/cases.json').read_text())};v2={x['id']:x for x in json.loads((B/'validation-02.json').read_text())};reviewinputs={x['id']:x for x in json.loads((B/'inputs/review-02/cases.json').read_text())}
for cid,h in continuation['prior_journal_hashes'].items():assert hashlib.sha256((B/'runs-generation'/f'{cid}.json').read_bytes()).hexdigest()==h
assert not set(continuation['pending_ids'])&set(continuation['prior_journal_hashes'])
for row in rows:
 cid=row['id']
 if cid not in v2:continue
 path=B/'runs-generation-02'/f'{cid}.json';g=json.loads(path.read_text()) if path.exists() else dict(status='not_run',elapsed_seconds=0);v=v2[cid]
 if path.exists():assert g['request']['messages']==[dict(role='system',content=inputs[cid]['system']),dict(role='user',content=inputs[cid]['user'])]
 u=g.get('response',{}).get('usage',{});row['generation']=dict(status=g['status'],valid=v['valid'],diagnostic=v.get('diagnostic'),answer_status=v.get('answer_status'),input_tokens=u.get('prompt_tokens'),output_tokens=u.get('completion_tokens'),elapsed_seconds=g['elapsed_seconds'],error=g.get('error'),model=g.get('response',{}).get('model'));review=None
 if cid in reviewinputs:
  p=B/'runs-review-02'/f'{cid}.json';q=json.loads(p.read_text()) if p.exists() else dict(status='not_run',elapsed_seconds=0)
  if p.exists():assert json.loads(q['request']['state'])=={k:reviewinputs[cid][k] for k in ('task','evidence','answer')}
  a=q.get('response',{}).get('answers',{});u=q.get('response',{}).get('usage',{});review=dict(status=q['status'],labels={k:a[k]['choice'] for k in a},input_tokens=u.get('input_tokens'),output_tokens=u.get('output_tokens'),elapsed_seconds=q['elapsed_seconds'],model=q.get('response',{}).get('model'))
 row['review']=review;row['usable_by_reviewer']=bool(v['valid'] and v.get('answer_status')=='answer' and review and review['status']=='completed' and review['labels']==dict(fidelity='supported',coverage='complete')) if review and review['status']=='completed' else None
summary={}
for method in ['equal','shared']:
 rr=[x for x in rows if x['method']==method];s=dict(planned=len(rr),attempted=sum(x['generation']['status']!='not_run' for x in rr),not_run=sum(x['generation']['status']=='not_run' for x in rr),failed=sum(x['generation']['status']=='failed' for x in rr),valid=sum(x['generation']['valid'] for x in rr),usable_observed=sum(x['usable_by_reviewer'] is True for x in rr),abstained=sum(x['generation']['answer_status']=='not_in_document' for x in rr),reviewed=sum(x['review'] and x['review']['status']=='completed' for x in rr if x['review']))
 for axis in ['generation','review']:
  for metric in ['input_tokens','output_tokens','elapsed_seconds']:s[axis+'_'+metric+'_observed']=round(sum((x[axis] or {}).get(metric) or 0 for x in rr),3)
 s['known_tokens']=sum(s[a+'_'+m+'_observed'] for a in ['generation','review'] for m in ['input_tokens','output_tokens']);summary[method]=s
pairs=[]
for oldpair in old['pairs']:
 rr={x['method']:x for x in rows if x['document_id']==oldpair['document_id']};a=rr['equal']['usable_by_reviewer'];b=rr['shared']['usable_by_reviewer'];pairs.append(dict(document_id=oldpair['document_id'],same_context=oldpair['same_context'],outcome='incomplete_pair' if a is None or b is None else 'shared_win' if b and not a else 'equal_win' if a and not b else 'both_usable' if a else 'neither_usable'))
health=json.loads((B/'health-01.json').read_text());result=dict(status='continuation_recorded',summary=summary,pairs=pairs,records=rows,prior_journals_unchanged=True,no_repeated_generation_ids=True,health=health,known_tokens_total=sum(x['known_tokens'] for x in summary.values())+health['usage']['total_tokens'],unknown_generation_usage_calls=sum(x['generation']['status']=='failed' and x['generation']['input_tokens'] is None for x in rows),generation_not_run=sum(x['generation']['status']=='not_run' for x in rows),limits='No retries; timeout usage unknown; Jev judgments not human adjudication; mixed execution dates; one draw per method')
(B/'result-resumed.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary));print([x['outcome'] for x in pairs]);print(result['known_tokens_total'])
