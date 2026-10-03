import json,sys,argparse
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();root=args.repo;sys.path.insert(0,str(root/'src'))
from agora.source import digest
from agora.plan_generation import generate
from agora.passage_view import display
from agora.qasper import render
from agora.structured_plan import prepare
from agora.source import FileSourceAdapter
p=args.out;p.mkdir(exist_ok=False)
f=json.loads((root/'experiments/section-comparison-v1/freeze.json').read_text())
data=(root/'experiments/qasper-v1/inputs/test.json').read_bytes();assert digest(data)==f['dataset_sha256']
doc=json.loads(data)['1901.05415'];structure={k:doc[k] for k in ['title','abstract','full_text']}
raw,_=render(structure);assert digest(raw)==f['cases'][0]['sha256'];(p/'source.txt').write_bytes(raw)
question=f['cases'][0]['questions'][0]['question']
spec={'schema':'agora/subquestions-input/v1-experimental','questions':[{'id':'P1','query':question,'reference_ranges':[]}]}
plan=prepare(FileSourceAdapter(p/'source.txt','1901.05415'),digest(raw),spec,structure,12000,6)
plan_bytes=(json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode();(p/'plan.json').write_bytes(plan_bytes);calls=[]
manual=json.loads((root/'experiments/focused-label-v1/repair/case.json').read_text())
def provider(system,user):
 payload=json.loads(user);units=payload['evidence_units'];texts=[u['text'] for u in units]
 coverage=[any(r['text'] in t for t in texts) for r in manual['ranges']];assert all(coverage)
 unit=next(u for u in units if 'Contexts with rating 1 were mapped' in u['text'])
 response={'finish_reason':'stop','content':json.dumps({'parts':[{'id':'P1','status':'partial','claims':[{'text':'La valoración 1 se asigna a la clase negativa.','evidence_ids':[unit['id']]}],'missing':['Rango positivo desconocido por fórmula faltante.']}]})}
 calls.append(dict(unit_count=len(units),manual_paragraphs_in_prompt=coverage,prompt_bytes=len(system.encode())+len(user.encode()),scope_instruction_present='selección es parcial' in payload['question']))
 (p/'fixture-response.json').write_text(json.dumps(response,indent=2)+'\n')
 return response
result=generate(p/'source.txt',plan_bytes,digest(plan_bytes),plan['questions'][0]['query'],provider,'ids',scope_guard=True)
assert result['execution_status']=='complete';assert result['requires_expansion'];assert result['parts'][0]['missing'];assert len(calls)==1
result.update(execution_origin='synthetic_provider_probe',http_attempts=0)
(p/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(p/'probe.json').write_text(json.dumps({'synthetic':True,'http_attempts':0,'provider_invocations':1,'checks':calls},indent=2)+'\n');view=display(result);assert view['missing']==result['parts'][0]['missing'];assert view['answer']==result['parts'][0]['claims'][0]['text'];assert view['requires_expansion'];(p/'view.json').write_text(json.dumps(view,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'passed','delivered_bytes':plan['delivered_bytes'],'http_attempts':0,'manual_paragraphs_in_prompt':calls[0]['manual_paragraphs_in_prompt'],'missing_visible':True}))
