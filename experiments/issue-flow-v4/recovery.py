"""Operación estable: no reenvío ciego ante resultado incierto."""
import importlib.util
import json
from pathlib import Path
BASE=Path(__file__).resolve().parent

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
storage=load('recovery_storage',BASE/'store.py')
flow=load('recovery_flow',BASE/'adapter.py')
Store=storage.Store
encode=storage.encode
digest=storage.digest
CONFIG=dict(model='glm-5.3-flash',temperature=0,max_tokens=8192,response_format={'type':'json_object'})
SYSTEM=storage.protocol.SYSTEM+'\n'+storage.protocol.envelope.POLICY

def provider_request(prepared):
 return dict(CONFIG,messages=[dict(role='system',content=SYSTEM),dict(role='user',content=encode(prepared['package']['input']))])

def inspect(store,operation_id):
 row=store.db.execute('SELECT digest,payload FROM operations WHERE id=?',(operation_id,)).fetchone()
 if row is None:return None
 op=json.loads(row[1])
 if digest(op)!=row[0] or op['id']!=operation_id or op['request_hash']!=digest(op['request']):raise ValueError('operation_integrity')
 if op['state'] not in ('attempted','response_ready','committed'):raise ValueError('operation_state')
 if op['state']=='committed':
  package=op['request']['prepared']['package'];history=store.history(package['issue'])
  match=[r for r in history if r['digest']==op['result']['revision_sha256']]
  if len(match)!=1 or match[0]['record']['parent']!=package['expected_head'] or match[0]['record']['input']!=package['input'] or match[0]['record']['model_content']!=op['response']['content'] or match[0]['record']['assessment']!=op['result']['assessment']:raise ValueError('operation_revision_mismatch')
 return op

def put(store,op):
 store.db.execute('INSERT INTO operations VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET digest=excluded.digest,payload=excluded.payload',(op['id'],digest(op),encode(op)))

def transaction(store,fn):
 store.db.execute('BEGIN IMMEDIATE')
 try:
  result=fn();store.db.execute('COMMIT');return result
 except Exception:
  if store.db.in_transaction:store.db.execute('ROLLBACK')
  raise

def reserve(store,operation_id,prepared):
 if type(operation_id) is not str or not operation_id.strip():raise ValueError('operation_id_required')
 request=json.loads(encode(dict(prepared=prepared,provider=provider_request(prepared))))
 def work():
  existing=inspect(store,operation_id)
  if existing:
   if existing['request_hash']!=digest(request):raise ValueError('operation_request_conflict')
   return existing,False
  flow.check_package(store,request['prepared'])
  op=dict(id=operation_id,state='attempted',request=request,request_hash=digest(request))
  put(store,op);return op,True
 return transaction(store,work)

def record_response(store,operation_id,response):
 # Se persiste aun si el contenido no pasa validación: no se reenvía.
 def work():
  op=inspect(store,operation_id)
  if op is None or op['state']!='attempted':raise ValueError('unexpected_operation_state')
  op.update(state='response_ready',response=json.loads(encode(response)));put(store,op)
 return transaction(store,work)

def finalize(store,operation_id):
 def work():
  op=inspect(store,operation_id)
  if op is None:raise ValueError('unknown_operation')
  if op['state']=='committed':return op['result']
  if op['state']!='response_ready':raise ValueError('provider_outcome_unknown')
  response=op['response'];package=op['request']['prepared']['package']
  if type(response) is not dict or response.get('finish_reason')!='stop':raise ValueError('incomplete_response')
  tokens=(response.get('usage') or {}).get('total_tokens')
  if type(tokens) is not int or tokens<0:raise ValueError('unknown_usage')
  candidate_content=encode(storage.protocol.prepare_candidate(response['content'],package['input']))
  candidate=storage.protocol.validate(candidate_content,package['input'])
  identity=store._append(package['issue'],package['expected_head'],package['input'],response['content'],candidate_content,dict(kind='model_candidate',operation_id=operation_id,request_sha256=op['request_hash'],model_reported=response.get('reported_model'),usage=response['usage'],admission='not_admitted'))
  result=dict(revision_sha256=identity,assessment=candidate,admission='not_admitted')
  op.update(state='committed',result=result);put(store,op);return result
 return transaction(store,work)

def evaluate(store,operation_id,prepared,provider):
 op,fresh=reserve(store,operation_id,prepared)
 if not fresh:
  if op['state']=='attempted':raise ValueError('provider_outcome_unknown')
  return finalize(store,operation_id)
 response=provider(json.loads(encode(op['request']['provider'])))
 record_response(store,operation_id,response)
 return finalize(store,operation_id)
