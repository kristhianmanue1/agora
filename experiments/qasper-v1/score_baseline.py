"""Score a completed frozen baseline; reads references only after generation."""
from pathlib import Path
import hashlib,json,importlib.util
from agora.qasper import verify,export_predictions
base=Path(__file__).resolve().parent;run=base/'runs/glm-baseline-01';prepared=base/'prepared/pilot-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
verify(prepared)
for n,h in json.loads((run/'freeze.json').read_text()).items():assert sha(run/n)==h,n
execution=json.loads((run/'execution.json').read_text());assert len(execution)==12
for row in execution:
 if row['result_sha256']:assert sha(run/row['case']/'result.json')==row['result_sha256']
meta=json.loads((base/'inputs/provenance.json').read_text());script=base/'inputs/evaluator.py'
assert sha(script)==meta['evaluator.py']['sha256']
spec=importlib.util.spec_from_file_location('official',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
export=export_predictions(prepared,run,run/'predictions.jsonl')
gold=m.get_answers_and_evidence(json.loads((prepared/'references/gold.json').read_text()),False)
pred={r['question_id']:{'answer':r['predicted_answer'],'evidence':r['predicted_evidence']} for r in map(json.loads,(run/'predictions.jsonl').read_text().splitlines())}
cases=json.loads((run/'model_inputs/cases.json').read_text());mapping=json.loads((prepared/'references/paragraphs.json').read_text());rows=[]
for c,e in zip(cases,execution):
 assert c['id']==e['case']
 r=json.loads((run/c['id']/'result.json').read_text()) if (run/c['id']/'result.json').exists() else {}
 metric=m.evaluate({c['question_id']:gold[c['question_id']]},pred)
 rows.append({'case':c['id'],'question_id':c['question_id'],'question':c['question'],'stratum':mapping[c['id']]['stratum'],'status':r.get('answer_status',r.get('diagnostic','missing')),'answer_f1':metric['Answer F1'],'evidence_f1':metric['Evidence F1'],'missing_predictions':metric['Missing predictions'],'abstained':r.get('unanswered_parts')==['answer'],'tokens':(e['usage'] or {}).get('total_tokens'),'seconds':e['seconds'],'reported_model':r.get('response',{}).get('reported_model')})
report={'official_evaluator_sha256':sha(script),'scope':'12-case diagnostic subset; not full QASPER','official_metrics':m.evaluate(gold,pred),'export':export,'rows':rows,'known_tokens':sum(r['tokens'] or 0 for r in rows),'unknown_usage_cases':[r['case'] for r in rows if r['tokens'] is None],'seconds':round(sum(r['seconds'] for r in rows),3),'freeze_verified':True}
with (run/'scores.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
