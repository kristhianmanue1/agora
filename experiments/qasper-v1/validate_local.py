"""Offline controls; no model calls, no benchmark score for Agora."""
from pathlib import Path
import hashlib,json,importlib.util,datetime
from collections import Counter
from agora.qasper import verify
from agora.source import FileSourceAdapter
from agora.routed_query import query_routed

base=Path(__file__).resolve().parent;inputs=base/'inputs'
meta=json.loads((inputs/'provenance.json').read_text()); evaluator=inputs/'evaluator.py'
assert hashlib.sha256(evaluator.read_bytes()).hexdigest()==meta['evaluator.py']['sha256']
spec=importlib.util.spec_from_file_location('official_qasper',evaluator);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
gold={'answerable':[{'answer':'Ada','evidence':['Ada leads.'],'type':'extractive'}],'absent':[{'answer':'Unanswerable','evidence':[],'type':'none'}]}
correct={'answerable':{'answer':'Ada','evidence':['Ada leads.']},'absent':{'answer':'Unanswerable','evidence':[]}}
wrong={'answerable':{'answer':'Bruno','evidence':['Bruno leads.']},'absent':{'answer':'Luna','evidence':['Luna approves.']}}
control={name:m.evaluate(gold,pred) for name,pred in [('correct',correct),('wrong',wrong),('missing',{})]}
assert control['correct']['Answer F1']==1 and control['correct']['Evidence F1']==1
assert control['wrong']['Answer F1']==0 and control['wrong']['Evidence F1']==0
assert control['missing']['Missing predictions']==2 and control['missing']['Answer F1']==0
prepared=base/'prepared/pilot-01';verify(prepared)
sel=json.loads((prepared/'references/selection.json').read_text());cases=json.loads((prepared/'model_inputs/cases.json').read_text())
summary={'counts':sel['counts'],'eligible_questions':sel['eligible_questions'],'exclusions':dict(Counter(x['reason'] for x in sel['excluded'])),'source_bytes':[len((prepared/'model_inputs'/c['source']).read_bytes()) for c in cases],'inspected_example_selected':any(c['question_id']=='397a1e851aab41c455c2b284f5e4947500d797f0' for c in cases)}
probes=[]
for c in cases:
 called=[]
 def fake(system,user):
  called.append(True)
  assert 'in English' in system
  assert set(json.loads(user))=={'question','parts','document'}
  return {'finish_reason':'stop','content':json.dumps({'parts':[{'id':'answer','status':'not_in_document','answer':'','quotes':[]}]})}
 r=query_routed(FileSourceAdapter(prepared/'model_inputs'/c['source'],c['source_id']),c['sha256'],c['question'],json.loads((prepared/'model_inputs'/c['parts']).read_text()),fake,full_source_budget=65536,prompt_budget=131072,response_language='en')
 assert r['execution_status']=='complete' and r['route']=='full_source' and len(called)==1
 probes.append({'case':c['id'],'prompt_bytes':r['prompt_bytes'],'route':r['route']})
report={'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_evaluator_sha256':meta['evaluator.py']['sha256'],'controls':control,'sample':summary,'fake_provider_preflight':probes,'network_model_calls':0,'semantic_evaluation':'not_performed','review':'producer self-review'}
out=base/'runs';out.mkdir(exist_ok=True)
with (out/'local-validation-01.json').open('x') as stream:json.dump(report,stream,indent=2)
print(json.dumps(report,indent=2))
