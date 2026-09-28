"""Preparación explícita y evaluación candidata; sin watcher ni admisión."""
from datetime import date
import hashlib
import importlib.util
import json
from pathlib import Path
STORE_PATH=Path(__file__).resolve().parent/'store.py'
spec=importlib.util.spec_from_file_location('flow_store',STORE_PATH)
store_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(store_module)
Store=store_module.Store
protocol=store_module.protocol
encode=store_module.encode
digest=store_module.digest

def prepare(store,issue,expected_head,new_source,as_of):
    if type(expected_head) is not str or not expected_head:raise ValueError('expected_head_required')
    history=store.history(issue,expected_head)
    if not history:raise ValueError('unknown_issue')
    source=json.loads(encode(new_source))
    if type(source) is not dict or set(source)!={'id','text','received_at','sha256'}:raise ValueError('invalid_source')
    if any(type(source[k]) is not str or not source[k].strip() for k in source):raise ValueError('invalid_source')
    if hashlib.sha256(source['text'].encode()).hexdigest()!=source['sha256']:raise ValueError('source_hash_mismatch')
    current=history[-1]['record']
    data=json.loads(encode(current['input']))
    if date.fromisoformat(as_of)<date.fromisoformat(data['as_of']) or date.fromisoformat(source['received_at'])>date.fromisoformat(as_of):raise ValueError('invalid_cutoff')
    if any(s['id']==source['id'] for s in data['sources']):raise ValueError('source_id_already_present')
    if any(s['sha256']==source['sha256'] for s in data['sources']):raise ValueError('duplicate_source_content')
    data['sources'].append(source);data['as_of']=as_of
    data['previous_assessment']=current['assessment']
    protocol.verify_bindings(data)
    package=dict(schema='agora/issue-evaluation-package/experimental-v4',issue=issue,expected_head=expected_head,new_source=source,input=data,validator_manifest=store_module.VALIDATOR_MANIFEST)
    return dict(package=package,sha256=digest(package))

def check_package(store,prepared):
    if type(prepared) is not dict or set(prepared)!={'package','sha256'} or digest(prepared['package'])!=prepared['sha256']:raise ValueError('package_integrity')
    package=prepared['package']
    rebuilt=prepare(store,package['issue'],package['expected_head'],package['new_source'],package['input']['as_of'])
    if encode(rebuilt)!=encode(prepared):raise ValueError('package_binding')
    return package
