"""Preparación explícita y evaluación candidata; sin watcher ni admisión."""
from datetime import date
import hashlib
import importlib.util
import json
from pathlib import Path
STORE_PATH=Path(__file__).resolve().parents[1]/'issue-store-v1/store.py'
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
    package=dict(schema='agora/issue-evaluation-package/experimental-v1',issue=issue,expected_head=expected_head,new_source=source,input=data,validator_sha256=store_module.VALIDATOR_HASH)
    return dict(package=package,sha256=digest(package))

def check_package(store,prepared):
    if type(prepared) is not dict or set(prepared)!={'package','sha256'} or digest(prepared['package'])!=prepared['sha256']:raise ValueError('package_integrity')
    package=prepared['package']
    rebuilt=prepare(store,package['issue'],package['expected_head'],package['new_source'],package['input']['as_of'])
    if rebuilt!=prepared:raise ValueError('package_binding')
    return package

def evaluate_and_record(store,prepared,provider):
    # Una instantánea separada evita mutaciones del caller durante el transporte.
    prepared=json.loads(encode(prepared));package=check_package(store,prepared)
    response=provider(protocol.SYSTEM,encode(package['input']))
    if type(response) is not dict or response.get('finish_reason')!='stop':raise ValueError('incomplete_response')
    usage=response.get('usage') or {};tokens=usage.get('total_tokens')
    if type(tokens) is not int or tokens<0:raise ValueError('unknown_usage')
    candidate=protocol.validate(response['content'],package['input'])
    identity=store.append(package['issue'],package['expected_head'],package['input'],response['content'],dict(kind='model_candidate',package_sha256=prepared['sha256'],response_sha256=digest(response),model_requested='glm-5.3-flash',model_reported=response.get('reported_model'),usage=usage,admission='not_admitted'))
    return dict(revision_sha256=identity,assessment=candidate,admission='not_admitted')
