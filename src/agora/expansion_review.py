"""Explicit claim-review ledger and retrieval plans; no automatic admission."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import urllib.request
from .source import FileSourceAdapter
from .passages import prepare as retrieve
from .issue_runtime import ROOT, load

API = load('agora_review_payload', ROOT/'experiments/reviewer-comparison-v2/run.py')
SCHEMA = 'agora/review-expansion/v1-experimental'
APP_ID = 0x41475245

def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()

def read(path):
    from .transform import unique_object
    value = json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        raise ValueError('json_object_required')
    return value

class Ledger:
    def __init__(self, path, create=False):
        path = Path(path)
        if create:
            with path.open('xb'):
                pass
        elif not path.is_file():
            raise ValueError('review_ledger_not_initialized')
        self.db = sqlite3.connect(f'{path.as_uri()}?mode=rw', uri=True, timeout=5)
        if create:
            with self.db:
                self.db.execute(f'PRAGMA application_id={APP_ID}')
                self.db.execute('PRAGMA user_version=1')
                self.db.execute('CREATE TABLE reviews (id TEXT PRIMARY KEY, body TEXT NOT NULL, digest TEXT NOT NULL)')
                self.db.execute('CREATE TABLE operations (id TEXT PRIMARY KEY, body TEXT NOT NULL, digest TEXT NOT NULL)')
        if self.db.execute('PRAGMA application_id').fetchone()[0] != APP_ID or self.db.execute('PRAGMA user_version').fetchone()[0] != 1:
            self.db.close()
            raise ValueError('incompatible_review_ledger')

    def close(self):
        self.db.close()

    def get(self, table, identity):
        if table not in ('reviews', 'operations'):
            raise ValueError('invalid_table')
        row = self.db.execute(f'SELECT body,digest FROM {table} WHERE id=?', (identity,)).fetchone()
        if row is None:
            return None
        body = json.loads(row[0])
        if digest(body) != row[1]:
            raise ValueError('record_integrity_mismatch')
        return dict(id=identity, record=body, sha256=row[1])

    def put(self, table, identity, body):
        if table not in ('reviews', 'operations') or not isinstance(identity, str) or not identity.strip() or len(identity)>200:
            raise ValueError('invalid_identity')
        self.db.execute(f'INSERT INTO {table} VALUES (?,?,?)', (identity, encode(body), digest(body)))
        return self.get(table, identity)

    def update_operation(self, identity, body):
        self.db.execute('UPDATE operations SET body=?,digest=? WHERE id=?', (encode(body), digest(body), identity))

def import_review(ledger, identity, data):
    if set(data) != {'schema','question','claim','evidence','provider','response'} or data['schema'] != 'agora/claim-review-input/v1-experimental':
        raise ValueError('invalid_review_input')
    for key in ('question','claim','evidence'):
        if not isinstance(data[key],str) or not data[key].strip():
            raise ValueError('invalid_review_text')
    provider = data['provider']
    if provider not in ('glm','jev'):
        raise ValueError('invalid_provider')
    support = API.engine.label(provider, data['response'])
    record = dict(schema=SCHEMA, **{k:data[k] for k in ('question','claim','evidence','provider','response')}, support=support,
                  origin='supplied_response', parent=None, admission='not_admitted')
    with ledger.db:
        existing = ledger.get('reviews',identity)
        if existing:
            if existing['record'] != record:
                raise ValueError('review_id_conflict')
            return existing
        return ledger.put('reviews',identity,record)

def prepare(ledger, parent_id, parent_sha, source, source_id, revision, budget, top_k):
    parent = ledger.get('reviews',parent_id)
    if parent is None or parent['sha256'] != parent_sha:
        raise ValueError('parent_revision_mismatch')
    original = parent['record']
    adapter = FileSourceAdapter(Path(source).resolve(), source_id)
    query = original['question']+'\n'+original['claim']
    envelope, metadata, _ = retrieve(adapter,revision,query,'retrieve',content_budget=budget,top_k=top_k)
    if envelope is None:
        raise ValueError('retrieval_budget_exhausted' if metadata['matching_paragraphs'] else 'no_retrieval_candidates')
    evidence = original['evidence']+''.join('\n\n'+s['text'] for s in envelope['spans'] if s['text'] != original['evidence'])
    plan = dict(schema=SCHEMA, parent_id=parent_id,parent_sha256=parent_sha,source_path=str(Path(source).resolve()),source_id=source_id,
                source_sha256=revision,budget=budget,top_k=top_k,query=query,envelope=envelope,retrieval=metadata,
                question=original['question'],claim=original['claim'],evidence=evidence,admission='not_admitted')
    if len(encode(plan).encode()) > 1024*1024:
        raise ValueError('plan_too_large')
    return dict(plan=plan,sha256=digest(plan))

def validate_plan(ledger, document, expected, check_source=True):
    if set(document) != {'plan','sha256'} or document['sha256']!=expected or digest(document['plan'])!=expected:
        raise ValueError('plan_digest_mismatch')
    plan = document['plan']
    if plan['schema']!=SCHEMA:
        raise ValueError('incompatible_plan')
    parent=ledger.get('reviews',plan['parent_id'])
    if parent is None or parent['sha256']!=plan['parent_sha256']:
        raise ValueError('parent_revision_mismatch')
    if check_source:
        rebuilt=prepare(ledger,plan['parent_id'],plan['parent_sha256'],plan['source_path'],plan['source_id'],plan['source_sha256'],plan['budget'],plan['top_k'])
        if rebuilt!=document:
            raise ValueError('plan_reproduction_mismatch')
    return plan

def key_for(provider):
    key = os.environ.get('TYPESAFE_API_KEY') if provider=='jev' else (os.environ.get('ZAI_API_KEY') or os.environ.get('SKOPOS_LLM_API_KEY'))
    if not key:
        raise ValueError('provider_key_missing')
    return key

def live(provider, plan):
    key=key_for(provider)
    url,payload=API.payload(provider,plan)
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):
            return None
    request=urllib.request.Request(url,data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
    with urllib.request.build_opener(NoRedirect()).open(request,timeout=90) as response:
        raw=response.read(1048577)
    if len(raw)>1048576 or key.encode() in raw:
        raise ValueError('invalid_provider_response')
    result=json.loads(raw)
    if provider=='glm':
        for choice in result.get('choices',[]):
            choice['message']={k:v for k,v in choice['message'].items() if k in ('role','content')}
    return result

def finalize(ledger, identity):
    ledger.db.execute('BEGIN IMMEDIATE')
    try:
        saved=ledger.get('operations',identity)
        if saved is None:
            raise ValueError('unknown_review_operation')
        op=saved['record']
        if op['state']=='attempted':
            raise ValueError('provider_outcome_unknown')
        if op['state']=='committed':
            review=ledger.get('reviews',identity)
            if review is None or review['sha256']!=op['result_sha256']:
                raise ValueError('committed_result_mismatch')
            ledger.db.commit()
            return review
        plan=validate_plan(ledger,op['document'],op['document']['sha256'],check_source=False)
        support=API.engine.label(op['provider'],op['response'])
        record=dict(schema=SCHEMA,question=plan['question'],claim=plan['claim'],evidence=plan['evidence'],provider=op['provider'],response=op['response'],support=support,
                    origin=op['origin'],parent={'id':plan['parent_id'],'sha256':plan['parent_sha256']},plan_sha256=op['document']['sha256'],admission='not_admitted')
        review=ledger.put('reviews',identity,record)
        op.update(state='committed',result_sha256=review['sha256']);ledger.update_operation(identity,op);ledger.db.commit()
        return review
    except Exception:
        ledger.db.rollback()
        raise

def evaluate(ledger, identity, document, expected, provider, response=None, call=None):
    if provider not in ('glm','jev'):
        raise ValueError('invalid_provider')
    if document.get('sha256')!=expected or digest(document.get('plan'))!=expected:
        raise ValueError('plan_digest_mismatch')
    origin='live_provider' if call else 'supplied_response_replay'
    request=dict(document=document,provider=provider,provider_request=API.payload(provider,document['plan'])[1],origin=origin,replay_sha256=digest(response) if not call else None)
    ledger.db.execute('BEGIN IMMEDIATE')
    try:
        old=ledger.get('operations',identity)
        if old:
            if old['record']['request_sha256']!=digest(request):
                raise ValueError('review_operation_conflict')
            ledger.db.commit()
            return finalize(ledger,identity)
        if ledger.get('reviews',identity):
            raise ValueError('review_id_conflict')
        validate_plan(ledger,document,expected)
        if call is live:
            key_for(provider)
        op=dict(request,state='attempted',request_sha256=digest(request))
        ledger.put('operations',identity,op);ledger.db.commit()
    except Exception:
        ledger.db.rollback()
        raise
    received=call(provider,document['plan']) if call else response
    # Keep invalid output before parsing. Only one writer can finalize the receipt.
    ledger.db.execute('BEGIN IMMEDIATE')
    try:
        current=ledger.get('operations',identity)['record']
        if current['state']!='attempted':
            raise ValueError('operation_state_conflict')
        current.update(state='response_ready',response=received);ledger.update_operation(identity,current);ledger.db.commit()
    except Exception:
        ledger.db.rollback();raise
    return finalize(ledger,identity)
