"""Durable repair derivatives; historical provider operations remain unchanged."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
BASE=Path(__file__).resolve().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
flow=load('derived_flow',BASE.parent/'issue-flow-v4/recovery.py')
repair=load('derived_format',BASE.parent/'output-format-v1/adapter.py')
encode=flow.encode
digest=flow.digest
FILES=['issue-flow-v4/store.py','issue-flow-v4/adapter.py','issue-flow-v4/recovery.py','open-issues-v4/protocol.py','skopos-issue-bridge-v2/envelope.py','skopos-issue-bridge-v1/bridge.py','output-format-v1/adapter.py']
MANIFEST={p:hashlib.sha256((BASE.parent/p).read_bytes()).hexdigest() for p in FILES}
APP_ID=0x41475231

def capture(source,operation_id,expected_head):
    if type(expected_head) is not str or not expected_head:raise ValueError('expected_head_required')
    source.db.execute('BEGIN')
    try:
        op=flow.inspect(source,operation_id)
        if op is None or op['state']!='response_ready':raise ValueError('response_not_ready')
        package=op['request']['prepared']['package']
        if package['expected_head']!=expected_head:raise ValueError('operation_base_mismatch')
        history=source.history(package['issue'],expected_head)
        flow.flow.check_package(source,op['request']['prepared'])
        return dict(operation=op,base=history[-1],captured_head=expected_head)
    finally:source.db.execute('ROLLBACK')

def derive(snapshot,receipt):
    snapshot=json.loads(encode(snapshot));receipt=json.loads(encode(receipt))
    if set(snapshot)!={'operation','base','captured_head'}:raise ValueError('invalid_snapshot')
    op=snapshot['operation'];base=snapshot['base'];record=base['record']
    if digest(record)!=base['digest'] or snapshot['captured_head']!=base['digest']:raise ValueError('base_integrity')
    if record['schema']!=flow.storage.SCHEMA or record['validator_manifest']!=flow.storage.VALIDATOR_MANIFEST:raise ValueError('validator_changed')
    for field in ('model_content','candidate_content'):
        key='model_content_sha256' if field=='model_content' else 'candidate_sha256'
        if repair.sha(record[field])!=record[key]:raise ValueError('base_content_integrity')
    checked=flow.storage.validate_adaptation(record['input'],record['model_content'],record['candidate_content'])
    if encode(checked)!=encode(record['assessment']):raise ValueError('base_assessment_mismatch')
    if op['state']!='response_ready' or digest(op['request'])!=op['request_hash']:raise ValueError('operation_integrity')
    prepared=op['request']['prepared'];package=prepared['package']
    if digest(package)!=prepared['sha256'] or package['expected_head']!=base['digest'] or package['issue']!=record['issue']:raise ValueError('request_binding')
    class Reader:
        def history(self,issue,head):
            if issue!=record['issue'] or head!=base['digest']:raise ValueError('snapshot_binding')
            return [base]
    rebuilt=flow.flow.prepare(Reader(),package['issue'],base['digest'],package['new_source'],package['input']['as_of'])
    if encode(rebuilt)!=encode(prepared) or encode(op['request']['provider'])!=encode(flow.provider_request(prepared)):raise ValueError('request_binding')
    response=op['response']
    if response.get('finish_reason')!='stop':raise ValueError('incomplete_response')
    tokens=(response.get('usage') or {}).get('total_tokens')
    if type(tokens) is not int or tokens<0:raise ValueError('unknown_usage')
    repair.verify(receipt)
    if receipt['status']!='repair_candidate' or receipt['original_content']!=response['content']:raise ValueError('repair_response_mismatch')
    candidate=flow.storage.protocol.prepare_candidate(receipt['candidate_content'],package['input'])
    result=flow.storage.protocol.validate(encode(candidate),package['input'])
    return dict(schema='agora/repaired-derivation/v1-experimental',kind='host_format_repair',snapshot=snapshot,receipt=receipt,candidate=candidate,assessment=result,parent_revision=base['digest'],origin_operation_id=op['id'],request_sha256=op['request_hash'],original_response_sha256=digest(response),validator_manifest=MANIFEST,admission='not_admitted',source_operation_state='response_ready')

class Store:
    def __init__(self,path,create=False):
        path=Path(path).resolve()
        if create:
            with path.open('xb'):pass
            path.chmod(0o600)
        self.db=sqlite3.connect(path.as_uri()+'?mode=rw',uri=True,isolation_level=None)
        try:
            self.db.execute('PRAGMA busy_timeout=3000');self.db.execute('PRAGMA synchronous=FULL')
            if create:self.db.executescript(f'BEGIN IMMEDIATE; PRAGMA application_id={APP_ID}; PRAGMA user_version=1; CREATE TABLE derivations(id TEXT PRIMARY KEY,digest TEXT NOT NULL,payload TEXT NOT NULL); COMMIT;')
            if self.db.execute('PRAGMA application_id').fetchone()[0]!=APP_ID or self.db.execute('PRAGMA user_version').fetchone()[0]!=1:raise ValueError('incompatible_store')
        except Exception:self.db.close();raise
    def close(self):self.db.close()
    def get(self,identity,expected_digest=None):
        row=self.db.execute('SELECT digest,payload FROM derivations WHERE id=?',(identity,)).fetchone()
        if row is None:
            if expected_digest is not None:raise ValueError('missing_derivation')
            return None
        checksum,payload=row;record=json.loads(payload,object_pairs_hook=flow.storage.protocol.unique)
        if digest(record)!=checksum or (expected_digest is not None and checksum!=expected_digest):raise ValueError('derivation_integrity')
        if record['validator_manifest']!=MANIFEST:raise ValueError('validator_changed')
        if encode(record)!=encode(derive(record['snapshot'],record['receipt'])):raise ValueError('derivation_binding')
        return dict(id=identity,digest=checksum,record=record)
    def put(self,identity,snapshot,receipt):
        if type(identity) is not str or not identity.strip():raise ValueError('derivation_id_required')
        record=derive(snapshot,receipt)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.get(identity)
            if prior is not None:
                if encode(prior['record'])!=encode(record):raise ValueError('derivation_request_conflict')
                self.db.execute('COMMIT');return prior
            checksum=digest(record)
            self.db.execute('INSERT INTO derivations VALUES(?,?,?)',(identity,checksum,encode(record)))
            self.db.execute('COMMIT');return dict(id=identity,digest=checksum,record=record)
        except Exception:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
