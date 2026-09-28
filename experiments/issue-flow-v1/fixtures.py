"""Pendiente sintético y nueva confirmación; sin fuentes reales."""
import hashlib
import json

def source(identity,text,received):return dict(id=identity,text=text,received_at=received,sha256=hashlib.sha256(text.encode()).hexdigest())
def inputs():
    old=source('q1','Coordinación: la fecha de entrega de Nube está pendiente. Lina es responsable.','2026-10-01')
    new=source('q2','Coordinación confirma: Nube se entrega el 2026-10-21. Lina sigue siendo responsable.','2026-10-08')
    data=dict(question='¿Fecha y responsable de entrega de Nube?',as_of='2026-10-01',requirements=dict(date=['date_confirmed'],owner=['owner_confirmed']),sources=[old],dependents=[],previous_assessment=None)
    def field(value,support,quote,missing):return dict(observed_value=value,support_status=support,missing_requirements=missing,relations=['initial'],change_source_ids=[],evidence=[dict(source_id='q1',quote=quote)])
    raw=json.dumps(dict(fields=dict(date=field(None,'missing','la fecha de entrega de Nube está pendiente',['date_confirmed']),owner=field('Lina','supported','Lina es responsable',[])),reason='Fecha pendiente; responsable explícita. Fixture manual.'))
    return data,raw,new

def valid_response():
    def field(value,quote,relation):return dict(observed_value=value,support_status='supported',missing_requirements=[],relations=[relation],change_source_ids=[],evidence=[dict(source_id='q2',quote=quote)])
    return dict(content=json.dumps(dict(fields=dict(date=field('2026-10-21','Nube se entrega el 2026-10-21','clarification'),owner=field('Lina','Lina sigue siendo responsable','duplicate')),reason='Fuente nueva confirma fecha y conserva responsable.')),finish_reason='stop',usage={'total_tokens':1},reported_model='test-double')
