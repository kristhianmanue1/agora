"""Recorded missing-value baseline plus a simulated clarification."""
import hashlib
import importlib.util
import json
from pathlib import Path

def seed(store):
    case=json.loads((Path(__file__).resolve().parents[1]/'open-issues-v4/replay-fixtures.json').read_text())[0]
    spec=importlib.util.spec_from_file_location("fixture_recovery",Path(__file__).resolve().parent/"recovery.py")
    recovery=importlib.util.module_from_spec(spec);spec.loader.exec_module(recovery)
    candidate=recovery.encode(recovery.storage.protocol.prepare_candidate(case['original_content'],case['input']))
    head=store.append('nube',None,case['input'],case['original_content'],candidate,dict(kind='historical_model_response_explicit_v4_adaptation'))
    text='Coordinación confirma: Nube se entrega el 2026-10-21. Lina sigue siendo responsable.'
    source=dict(id='new-confirmation',text=text,received_at='2026-10-09',sha256=hashlib.sha256(text.encode()).hexdigest())
    return head,source

def provider(request):
    data=json.loads(request['messages'][1]['content'])
    def field(value,quote):
        return dict(observed_value=value,support_status='supported',missing_requirements=[],relations=['clarification'],change_source_ids=[],evidence=[dict(source_id='new-confirmation',quote=quote)])
    return dict(content=json.dumps(dict(fields=dict(date=field('2026-10-21','Nube se entrega el 2026-10-21'),owner=field('Lina','Lina sigue siendo responsable')),reason='Simulated clarification; no semantic model evaluation.')),finish_reason='stop',usage={'total_tokens':0},reported_model='test-double')
