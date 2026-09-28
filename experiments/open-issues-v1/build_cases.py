"""Fixtures sintéticos explícitos; no contienen datos de reuniones reales."""
import json
from pathlib import Path
BASE = Path(__file__).resolve().parent

def source(identity, text, **extra):
    return dict(id=identity, text=text, **extra)

def expected(status, relation, values, affected=None):
    return dict(status=status, relation=relation, values=values, affected=affected or [])

cases = [
 dict(id='clarification', question='¿Fecha de entrega del proyecto Alba?', fields=['date'],
      criterion='Fecha explícita de entrega de Alba confirmada por coordinación.',
      sources=[source('a1','Coordinación: falta definir la fecha de entrega de Alba.'),
               source('a2','Coordinación: confirmo entrega de Alba el 2026-10-09.')], dependents=[]),
 dict(id='partial', question='¿Fecha y responsable de entrega de Alba?', fields=['date','owner'],
      criterion='Se necesitan fecha y responsable explícitos para cerrar todo el pendiente.',
      sources=[source('b1','Coordinación: fecha y responsable de Alba pendientes.'),
               source('b2','Coordinación: Alba se entrega el 2026-10-09. Responsable aún pendiente.')], dependents=[]),
 dict(id='irrelevant', question='¿Fecha de entrega de Alba?', fields=['date'],
      criterion='Sólo una fecha para Alba resuelve la pregunta.',
      sources=[source('c1','Coordinación: no hay fecha definida para Alba.'),
               source('c2','Coordinación: el proyecto Brisa se entrega el 2026-10-09; Alba sigue pendiente.')], dependents=[]),
 dict(id='duplicate', question='¿Está corroborada la entrega de Alba el 2026-10-09?', fields=['date'],
      criterion='Requiere dos confirmaciones de origen independiente. Una copia no cuenta. Mientras falte corroboración, date=null.',
      sources=[source('d1','Informe de coordinación: Alba se entrega el 2026-10-09.', origin='coordination-report'),
               source('d2','El boletín copia el informe de coordinación: Alba se entrega el 2026-10-09.', origin='coordination-report', copied_from='d1')], dependents=[]),
 dict(id='update', question='¿Fecha vigente de entrega de Alba?', fields=['date'],
      criterion='La coordinación puede cambiar la fecha. Conservar el acuerdo histórico; marcar para revisión el aviso derivado de la fecha anterior.',
      sources=[source('e1','2026-09-01. Coordinación fija entrega de Alba el 2026-10-09.'),
               source('e2','2026-09-05. Coordinación cambia la entrega de Alba al 2026-10-16. El acuerdo anterior fue válido hasta este cambio.')],
      dependents=[dict(id='notice', source_ids=['e1'], description='Aviso de entrega vigente basado en e1')]),
 dict(id='refutation', question='¿Fecha confirmada de entrega de Alba?', fields=['date'],
      criterion='Una rectificación que retira la única fecha reabre el pendiente y exige revisar el aviso dependiente.',
      sources=[source('f1','Coordinación confirma entrega de Alba el 2026-10-09.'),
               source('f2','Coordinación rectifica f1: la fecha 2026-10-09 fue un error de transcripción. No hay fecha aprobada de entrega de Alba.')],
      dependents=[dict(id='notice', source_ids=['f1'], description='Aviso de entrega vigente basado en f1')]),
]
gold = {
 'clarification':[expected('open','initial',dict(date=None)),expected('resolved','clarification',dict(date='2026-10-09'))],
 'partial':[expected('open','initial',dict(date=None,owner=None)),expected('partial','partial',dict(date='2026-10-09',owner=None))],
 'irrelevant':[expected('open','initial',dict(date=None)),expected('open','irrelevant',dict(date=None))],
 'duplicate':[expected('open','initial',dict(date=None)),expected('open','duplicate',dict(date=None))],
 'update':[expected('resolved','initial',dict(date='2026-10-09')),expected('resolved','update',dict(date='2026-10-16'),['notice'])],
 'refutation':[expected('resolved','initial',dict(date='2026-10-09')),expected('reopened','refutation',dict(date=None),['notice'])],
}
if __name__ == '__main__':
 for name, value in [('cases',cases),('gold',gold)]:
  (BASE/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
