import json
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=R/'experiments/retrieval-answer-paired-v1';key=json.loads((B/'key.json').read_text());vals=json.loads((B/'validation.json').read_text())
for v in vals:
 if v['transport_status']=='not_run':v['diagnostic']='not_run_after_three_errors'
(B/'validation.json').write_text(json.dumps(vals,indent=2)+'\n');validation={x['id']:x for x in vals};inputs={x['id']:x for x in json.loads((B/'inputs/cases.json').read_text())};reviewinputs={x['id']:x for x in json.loads((B/'inputs/review/cases.json').read_text())};rows=[]
for k in key:
 cid=k['id'];p=B/'runs-generation'/f'{cid}.json';g=json.loads(p.read_text()) if p.exists() else dict(status='not_run',elapsed_seconds=0);v=validation[cid]
 if p.exists():assert g['request']['messages']==[dict(role='system',content=inputs[cid]['system']),dict(role='user',content=inputs[cid]['user'])]
 usage=g.get('response',{}).get('usage',{});generation=dict(status=g['status'],valid=v['valid'],diagnostic=v.get('diagnostic'),answer_status=v.get('answer_status'),input_tokens=usage.get('prompt_tokens'),output_tokens=usage.get('completion_tokens'),elapsed_seconds=g['elapsed_seconds'],error=g.get('error'),model=g.get('response',{}).get('model'));review=None
 if cid in reviewinputs:
  q=json.loads((B/'runs-review'/f'{cid}.json').read_text());assert json.loads(q['request']['state'])=={z:reviewinputs[cid][z] for z in ('task','evidence','answer')};a=q.get('response',{}).get('answers',{});ru=q.get('response',{}).get('usage',{});review=dict(status=q['status'],labels={z:a[z]['choice'] for z in a},input_tokens=ru.get('input_tokens'),output_tokens=ru.get('output_tokens'),elapsed_seconds=q['elapsed_seconds'],model=q.get('response',{}).get('model'))
 usable=bool(v['valid'] and v.get('answer_status')=='answer' and review and review['status']=='completed' and review['labels']==dict(fidelity='supported',coverage='complete'))
 rows.append(dict(id=cid,document_id=k['document_id'],method=k['method'],delivered_bytes=k['delivered_bytes'],retrieval_seconds=k['retrieval_seconds'],generation=generation,review=review,usable_by_reviewer=usable if review else None))
summary={}
for method in ['equal','shared']:
 rr=[x for x in rows if x['method']==method];s=dict(planned=len(rr),attempted=sum(x['generation']['status']!='not_run' for x in rr),not_run=sum(x['generation']['status']=='not_run' for x in rr),failed=sum(x['generation']['status']=='failed' for x in rr),valid=sum(x['generation']['valid'] for x in rr),usable_observed=sum(x['usable_by_reviewer'] is True for x in rr),review_calls=sum(x['review'] is not None for x in rr),retrieval_bytes_all_prepared=sum(x['delivered_bytes'] for x in rr),retrieval_seconds=sum(x['retrieval_seconds'] for x in rr))
 for axis in ['generation','review']:
  for metric in ['input_tokens','output_tokens','elapsed_seconds']:s[axis+'_'+metric+'_observed']=round(sum((x[axis] or {}).get(metric) or 0 for x in rr),3)
 s['tokens_observed_lower_bound']=sum(s[a+'_'+m+'_observed'] for a in ['generation','review'] for m in ['input_tokens','output_tokens']);summary[method]=s
pairs=[]
for pid in dict.fromkeys(x['document_id'] for x in rows):
 rr={x['method']:x for x in rows if x['document_id']==pid};a=rr['equal']['usable_by_reviewer'];c=rr['shared']['usable_by_reviewer'];env=[]
 for method in ['equal','shared']:env.append(json.loads((B/'inputs'/f"{rr[method]['id']}-envelope.json").read_text())['spans'])
 pairs.append(dict(document_id=pid,same_context=env[0]==env[1],outcome='incomplete_pair' if a is None or c is None else 'shared_win' if c and not a else 'equal_win' if a and not c else 'both_usable' if a else 'neither_usable'))
result=dict(status='partial_transport_stop',stop='inherited runner stopped after three transport timeouts; no retries',summary=summary,pairs=pairs,records=rows,known_tokens_total=sum(x['tokens_observed_lower_bound'] for x in summary.values()),unknown_usage_calls=3,monetary_cost='unverified; timeout calls may incur unreported usage',blinding='reviewer received task, full evidence, answer only; method/gold/sibling absent; neutral IDs and shuffled order')
(B/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary));print('known tokens',result['known_tokens_total']);print('pair outcomes',[p['outcome'] for p in pairs])
