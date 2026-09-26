"""Fixed official metrics plus descriptive paired counts; no semantic judge."""
from pathlib import Path
import hashlib,json,importlib.util
from agora.qasper import verify,export_predictions
b=Path(__file__).resolve().parent;run=b/'runs/glm-paired-01';prepared=b/'prepared/pilot-02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
verify(prepared)
for n,h in json.loads((run/'freeze.json').read_text()).items():assert sha(run/n)==h,n
execution=json.loads((run/'execution.json').read_text());assert len(execution)==24
for r in execution:
 if r['result_sha256']:assert sha(run/r['profile']/r['case']/'result.json')==r['result_sha256']
script=b/'inputs/evaluator.py';assert sha(script)==json.loads((b/'inputs/provenance.json').read_text())['evaluator.py']['sha256']
spec=importlib.util.spec_from_file_location('official',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
gold=m.get_answers_and_evidence(json.loads((prepared/'references/gold.json').read_text()),False)
cases=json.loads((prepared/'model_inputs/cases.json').read_text());mapping=json.loads((prepared/'references/paragraphs.json').read_text());reports={}
for profile in ['legacy','concise-v1']:
 out=run/profile;export=export_predictions(prepared,out,out/'predictions.jsonl')
 pred={r['question_id']:{'answer':r['predicted_answer'],'evidence':r['predicted_evidence']} for r in map(json.loads,(out/'predictions.jsonl').read_text().splitlines())}
 rows=[]
 for c in cases:
  e=next(e for e in execution if e['case']==c['id'] and e['profile']==profile);f=out/c['id']/'result.json';r=json.loads(f.read_text()) if f.exists() else {};p=(r.get('parts') or [{}])[0]
  score=m.evaluate({c['question_id']:gold[c['question_id']]},pred)
  rows.append({'case':c['id'],'question':c['question'],'stratum':mapping[c['id']]['stratum'],'execution_status':r.get('execution_status','missing'),'status':p.get('status'),'answer':p.get('answer'),'explanation':p.get('explanation'),'answer_chars':len(p.get('answer','')),'answer_f1':score['Answer F1'],'evidence_f1':score['Evidence F1'],'tokens':(e['usage'] or {}).get('total_tokens'),'seconds':e['seconds']})
 reports[profile]={'official_metrics':m.evaluate(gold,pred),'export':export,'rows':rows,'correct_abstentions':sum(r['stratum']=='unanswerable' and r['status']=='not_in_document' for r in rows),'false_abstentions':sum(r['stratum']=='answerable' and r['status']=='not_in_document' for r in rows),'known_tokens':sum(r['tokens'] or 0 for r in rows),'unknown_usage_cases':[r['case'] for r in rows if r['tokens'] is None],'seconds':round(sum(r['seconds'] for r in rows),3)}
report={'scope':'12 document-disjoint pairs; one generation per condition; no inferential superiority claim','official_evaluator_sha256':sha(script),'profiles':reports}
with (run/'scores.json').open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps({k:{x:y for x,y in v.items() if x!='rows'} for k,v in reports.items()},indent=2))
