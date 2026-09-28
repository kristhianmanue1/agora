"""SQLite v4 candidate consumer; explicit adaptation, no legacy migration."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3

BASE=Path(__file__).resolve().parent
PROTOCOL=BASE.parent/'open-issues-v4/protocol.py'
spec=importlib.util.spec_from_file_location('store_v4_protocol',PROTOCOL)
protocol=importlib.util.module_from_spec(spec);spec.loader.exec_module(protocol)
APP_ID=0x41474935
VERSION=5
SCHEMA='agora/issue-revision/experimental-v4'
VALIDATOR_FILES=[PROTOCOL,BASE.parent/'skopos-issue-bridge-v2/envelope.py',BASE.parent/'skopos-issue-bridge-v1/bridge.py']
VALIDATOR_MANIFEST={str(p.relative_to(BASE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in VALIDATOR_FILES}

def encode(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)

def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()

def validate_adaptation(data,model_content,candidate_content):
    candidate=json.loads(candidate_content,object_pairs_hook=protocol.unique)
    expected=protocol.prepare_candidate(model_content,data)
    if encode(candidate)!=encode(expected):raise ValueError('adaptation_mismatch')
    return protocol.validate(candidate_content,data)

class Store:
    def __init__(self,path,create=False):
        path=Path(path).resolve()
        if create:
            with path.open('xb'):pass
            path.chmod(0o600)
        self.db=sqlite3.connect(path.as_uri()+'?mode=rw',uri=True,isolation_level=None)
        try:
            self.db.execute('PRAGMA busy_timeout=3000')
            self.db.execute('PRAGMA synchronous=FULL')
            if create:
                self.db.executescript(f'BEGIN IMMEDIATE; PRAGMA application_id={APP_ID}; PRAGMA user_version={VERSION}; CREATE TABLE revisions(issue TEXT NOT NULL, revision INTEGER NOT NULL, digest TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(issue,revision)); CREATE TABLE operations(id TEXT PRIMARY KEY, digest TEXT NOT NULL, payload TEXT NOT NULL); COMMIT;')
            if self.db.execute('PRAGMA application_id').fetchone()[0]!=APP_ID or self.db.execute('PRAGMA user_version').fetchone()[0]!=VERSION:
                raise ValueError('incompatible_store')
        except Exception:
            self.db.close();raise

    def close(self):self.db.close()

    def history(self,issue,expected_head=None):
        # One SELECT yields a coherent snapshot of all records for this issue.
        rows=self.db.execute('SELECT revision,digest,payload FROM revisions WHERE issue=? ORDER BY revision',(issue,)).fetchall()
        history=[];parent=None
        for index,(number,checksum,payload) in enumerate(rows,1):
            record=json.loads(payload,object_pairs_hook=protocol.unique)
            if record.get('schema')!=SCHEMA or number!=index or record.get('revision')!=index or record.get('issue')!=issue or record.get('parent')!=parent or digest(record)!=checksum:
                raise ValueError('history_integrity')
            if record['validator_manifest']!=VALIDATOR_MANIFEST:raise ValueError('validator_changed')
            if record['model_content_sha256']!=hashlib.sha256(record['model_content'].encode()).hexdigest():raise ValueError('model_content_integrity')
            if record['candidate_sha256']!=hashlib.sha256(record['candidate_content'].encode()).hexdigest():raise ValueError('candidate_integrity')
            checked=validate_adaptation(record['input'],record['model_content'],record['candidate_content'])
            if encode(checked)!=encode(record['assessment']):raise ValueError('assessment_mismatch')
            history.append(dict(digest=checksum,record=record));parent=checksum
        if expected_head is not None and parent!=expected_head:raise ValueError('head_mismatch')
        return history

    def append(self,issue,expected_head,data,model_content,candidate_content,provenance):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            result=self._append(issue,expected_head,data,model_content,candidate_content,provenance)
            self.db.execute('COMMIT');return result
        except Exception:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def _append(self,issue,expected_head,data,model_content,candidate_content,provenance):
        if not self.db.in_transaction:raise ValueError('transaction_required')
        if type(issue) is not str or not issue.strip() or type(provenance) is not dict or not provenance:raise ValueError('invalid_identity')
        data=json.loads(encode(data));provenance=json.loads(encode(provenance))
        checked=validate_adaptation(data,model_content,candidate_content)
        history=self.history(issue)
        parent=history[-1]['digest'] if history else None
        if parent!=expected_head:raise ValueError('stale_parent')
        if history and any(data[k]!=history[0]['record']['input'][k] for k in ('question','requirements')):raise ValueError('issue_definition_changed')
        record=dict(schema=SCHEMA,issue=issue,revision=len(history)+1,parent=parent,input=data,model_content=model_content,model_content_sha256=hashlib.sha256(model_content.encode()).hexdigest(),candidate_content=candidate_content,candidate_sha256=hashlib.sha256(candidate_content.encode()).hexdigest(),assessment=checked,provenance=provenance,adaptation='host_schema_and_supplied_scope_only',admission='not_admitted',validator_manifest=VALIDATOR_MANIFEST)
        checksum=digest(record)
        self.db.execute('INSERT INTO revisions VALUES(?,?,?,?)',(issue,record['revision'],checksum,encode(record)))
        return checksum
