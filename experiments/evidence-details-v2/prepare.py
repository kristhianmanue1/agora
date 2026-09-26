"""Freeze known regression plus new controls before any v2 model call."""
from pathlib import Path
import json,shutil
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter,digest
b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'inputs';out.mkdir(exist_ok=False)
old=root/'experiments/evidence-review-v1/runs/format-02/N2-1024.json'
shutil.copyfile(old,out/'R-regression.json')
cases=[{'id':'R-regression','expected_support':{'2':'insufficient'},'expected_relevance':{'5':'extra'},'kind':'known real QASPER regression; other claims not adjudicated'}]
fixtures=[
 ('C-population','En 2024 se observó una reducción media del 4% en 300 adultos urbanos.',
 '¿Qué población y resultado se observaron?',
 ['En 2024 se observó una reducción media del 4% en 300 adultos urbanos.',
  'En 2024 se observó una reducción media del 4% en 300 adultos urbanos y rurales.'],['supported','insufficient']),
 ('C-negation','El comité rechazó la compra y no autorizó el pago.',
 '¿Qué decidió el comité sobre compra y pago?',
 ['El comité rechazó la compra y no autorizó el pago.',
  'El comité aprobó la compra y autorizó el pago.'],['supported','contradicted']),
 ('C-condition','La reducción media fue del 4%, exclusivamente en casos leves. En casos graves no hubo reducción.',
 '¿En qué casos hubo reducción y de cuánto fue?',
 ['La reducción media fue del 4% en casos leves; en casos graves no hubo reducción.',
  'La reducción media fue del 4% en todos los casos, incluidos los graves.'],['supported','contradicted']),
]
for cid,text,question,claims,expected in fixtures:
 p=out/(cid+'.txt');p.write_text(text)
 parts={'parts':[{'id':'answer','status':'answered','claims':[{'text':c,'quotes':[text]} for c in claims],'missing':[]}]}
 candidate=query_evidence(FileSourceAdapter(p,cid),digest(p.read_bytes()),question,[{'id':'answer','question':question}],lambda s,u:{'finish_reason':'stop','content':json.dumps(parts)})
 assert candidate['execution_status']=='complete';(out/(cid+'.json')).write_text(json.dumps(candidate,indent=2))
 cases.append({'id':cid,'expected_support':{str(i):s for i,s in enumerate(expected)},'kind':'new synthetic fixture; no producer model call'})
(out/'cases.json').write_text(json.dumps(cases,indent=2))
print(json.dumps(cases))
