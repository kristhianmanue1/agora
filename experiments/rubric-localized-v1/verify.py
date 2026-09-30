"""Offline verification of frozen inputs, provider receipts and response validation."""
import json,hashlib,importlib.util,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.qasper import render
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=load(B/'freeze.json');old=B.parent/'rubric-reserved-v1';original=load(old/'freeze.json');ds=B.parent/'qasper-v1/inputs/test.json';assert sha(ds)==original['dataset_sha256'];source,paras=render(load(ds)[original['document_id']]);assert hashlib.sha256(source).hexdigest()==f['source_sha256'];assert sha(old/'rubric.json')==f['rubric_sha256']
for name in ('run','check_jev'):
 spec=importlib.util.spec_from_file_location(name,B/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 journal=B/('runs-critique/localized-critique.json' if name=='run' else 'runs-check/localized-check.json');record=load(journal)
 label=m.label('glm' if name=='run' else 'jev',record['response']);assert label==('adequate' if name=='run' else 'none_demonstrated')
 assert hashlib.sha256(json.dumps(record['request'],ensure_ascii=False).encode()).hexdigest()==record['request_sha256']
assert sha(B/'inputs/cases.json')==f['cases_sha256'];assert sha(B/'inputs/jev/cases.json')==load(B/'jev-freeze.json')['cases_sha256']
state=load(B/'inputs/cases.json')[0]['state'];assert set(state)=={'task','requirements','source_units','reference_annotations'}
for u in state['source_units']:assert source[u['start_byte']:u['end_byte']].decode()==u['text']
assert state==load(B/'inputs/jev/cases.json')[0]['state']
r=load(B/'glm-validation.json');assert r['original_journal_sha256']==sha(B/'runs-critique/localized-critique.json');assert r['http_calls']==0
print('OK: frozen source/rubric, 28 locators, blinded states, response schemas and unchanged original journal; zero HTTP')
