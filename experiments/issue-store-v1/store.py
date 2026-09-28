"""Historial SQLite local: revisiones candidatas, no memoria admitida."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
PROTOCOL=Path(__file__).resolve().parents[1]/'open-issues-v3/protocol.py'
spec=importlib.util.spec_from_file_location('issue_store_protocol',PROTOCOL)
protocol=importlib.util.module_from_spec(spec);spec.loader.exec_module(protocol)
VALIDATOR_HASH=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
APP_ID=0x41474931

def encode(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(encode(value).encode()).hexdigest()

class Store:
 def __init__(self,path,create=False):
  path=Path(path).resolve()
  if create:
   with path.open('xb'):pass
  self.db=sqlite3.connect(path.as_uri()+'?mode=rw',uri=True,isolation_level=None)
  try:
   self.db.execute('PRAGMA busy_timeout=3000')
   self.db.execute('PRAGMA synchronous=FULL')
   if create:
    self.db.executescript(f'BEGIN IMMEDIATE; PRAGMA application_id={APP_ID}; PRAGMA user_version=1; CREATE TABLE revisions(issue TEXT NOT NULL, revision INTEGER NOT NULL, digest TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(issue,revision)); COMMIT;')
   if self.db.execute('PRAGMA application_id').fetchone()[0]!=APP_ID or self.db.execute('PRAGMA user_version').fetchone()[0]!=1:raise ValueError('foreign_store')
  except Exception:
   self.db.close();raise
 def close(self):self.db.close()
 def history(self,issue,expected_head=None):
  rows=self.db.execute('SELECT revision,digest,payload FROM revisions WHERE issue=? ORDER BY revision',(issue,)).fetchall()
  result=[];parent=None
  for number,(revision,stored_hash,payload) in enumerate(rows,1):
   record=json.loads(payload)
   if revision!=number or record.get('revision')!=number or record.get('issue')!=issue or record.get('parent')!=parent or digest(record)!=stored_hash:raise ValueError('history_integrity')
   if record['validator_sha256']!=VALIDATOR_HASH:raise ValueError('validator_changed')
   checked=protocol.validate(record['raw_response'],record['input'])
   if checked!=record['assessment']:raise ValueError('assessment_mismatch')
   result.append(dict(digest=stored_hash,record=record));parent=stored_hash
  if expected_head is not None and parent!=expected_head:raise ValueError('head_mismatch')
  return result
 def append(self,issue,expected_head,data,raw_response,provenance):
  if type(issue) is not str or not issue.strip() or type(provenance) is not dict or not provenance:raise ValueError('invalid_identity')
  # Copia JSON evita que una mutación del caller cambie lo validado y persistido.
  data=json.loads(encode(data));provenance=json.loads(encode(provenance))
  checked=protocol.validate(raw_response,data)
  self.db.execute('BEGIN IMMEDIATE')
  try:
   history=self.history(issue)
   parent=history[-1]['digest'] if history else None
   if parent!=expected_head:raise ValueError('stale_parent')
   if history and any(data[k]!=history[0]['record']['input'][k] for k in ('question','requirements')):raise ValueError('issue_definition_changed')
   record=dict(schema='agora/issue-revision/experimental-v1',issue=issue,revision=len(history)+1,parent=parent,input=data,raw_response=raw_response,assessment=checked,provenance=provenance,validator_sha256=VALIDATOR_HASH)
   identity=digest(record)
   self.db.execute('INSERT INTO revisions VALUES(?,?,?,?)',(issue,record['revision'],identity,encode(record)))
   self.db.execute('COMMIT')
   return identity
  except Exception:
   self.db.execute('ROLLBACK');raise
