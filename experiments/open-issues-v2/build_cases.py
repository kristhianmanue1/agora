"""Nuevos casos de perturbación; expectativas fijadas antes de llamar al modelo."""
import json
from pathlib import Path
BASE=Path(__file__).resolve().parent

def s(i,text,at):return dict(id=i,text=text,received_at=at)
def prior(date,owner='Lina'):
 return dict(status='resolved',fields={k:dict(observed_value=v,support_status='supported',missing_requirements=[],relations=['initial'],evidence=[]) for k,v in dict(date=date,owner=owner).items()},reason='Evaluación anterior guardada; su corrección no está garantizada.')
def gold(date,owner,withdrawn=False,affected=None):
 values=dict(date=date,owner=owner)
 support={k:'supported' if v else 'withdrawn' if withdrawn and k=='date' else 'missing' for k,v in values.items()}
 return dict(status='resolved' if all(values.values()) else 'partial' if any(values.values()) else 'open',values=values,support=support,missing={k:[] if v else [k+'_confirmed'] for k,v in values.items()},affected=affected or [],reopened_fields=['date'] if withdrawn else [])
common=dict(question='¿Fecha y responsable vigentes de entrega de Nube?',as_of='2026-10-10',requirements=dict(date=['date_confirmed'],owner=['owner_confirmed']))
cases=[
 dict(common,id='wrong_history',sources=[s('w1','Coordinación: Nube se entrega el 2026-10-21. La responsable es Lina.','2026-10-01')],dependents=[],prior=prior('2026-11-30','Marco')),
 dict(common,id='late_source',sources=[s('l1','Decisión del 2026-10-05: la entrega de Nube cambia del 2026-10-14 al 2026-10-21. Responsable Lina.','2026-10-05'),s('l2','Acta del 2026-09-20: Nube se entregará el 2026-10-14; responsable Lina. Este acta registra únicamente lo acordado ese día.','2026-10-09')],dependents=[],prior=prior('2026-10-21')),
 dict(common,id='partial_refutation',sources=[s('p1','Coordinación: Nube se entrega el 2026-10-21 y Lina es responsable.','2026-10-01'),s('p2','Coordinación rectifica: la fecha de p1 es un error, no existe fecha aprobada para Nube. Lina sigue siendo responsable.','2026-10-08')],dependents=[dict(id='schedule',fields=['date']),dict(id='assignment',fields=['owner'])],prior=prior('2026-10-21')),
 dict(common,id='unaffected_dependent',sources=[s('u1','Coordinación: Nube se entrega el 2026-10-21; responsable Lina.','2026-10-01'),s('u2','Coordinación: Nube se entregará el 2026-10-28 en sustitución de la fecha anterior. La responsable sigue siendo Lina.','2026-10-08')],dependents=[dict(id='schedule',fields=['date']),dict(id='assignment',fields=['owner'])],prior=prior('2026-10-21')),
]
expected={'wrong_history':[gold('2026-10-21','Lina')],'late_source':[gold('2026-10-21','Lina')],'partial_refutation':[gold(None,'Lina',True,['schedule'])],'unaffected_dependent':[gold('2026-10-28','Lina',affected=['schedule'])]}
if __name__=='__main__':
 for name,value in [('cases',cases),('gold',expected)]: (BASE/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
