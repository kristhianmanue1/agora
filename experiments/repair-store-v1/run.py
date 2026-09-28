"""Copy the failed database; persist a separate derivative and recover lost ack."""
import hashlib,json,os,sqlite3,subprocess,sys
from pathlib import Path
from store import Store,capture,flow,repair
BASE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    if sys.argv[1]=='child':
        out=Path(sys.argv[2]);source=flow.Store(out/'source-copy.sqlite3')
        try:snapshot=capture(source,'live-v4-001',sys.argv[3])
        finally:source.close()
        store=Store(out/'derivations.sqlite3')
        try:store.put('repair-001',snapshot,repair.propose(snapshot['operation']['response']['content']))
        finally:store.close()
        raise SystemExit(7)
    if sys.argv[1]=='read':
        store=Store(sys.argv[2])
        try:print(flow.encode(store.get('repair-001',sys.argv[3])))
        finally:store.close()
        return
    original=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();os.umask(0o077);out.mkdir(parents=True,exist_ok=False)
    original_hash=sha(original);source=sqlite3.connect(original.as_uri()+'?mode=ro',uri=True);copy=sqlite3.connect(out/'source-copy.sqlite3')
    try:source.backup(copy)
    finally:copy.close();source.close()
    copy_hash=sha(out/'source-copy.sqlite3');source=flow.Store(out/'source-copy.sqlite3')
    try:
        op=flow.inspect(source,'live-v4-001');head=op['request']['prepared']['package']['expected_head'];snapshot=capture(source,'live-v4-001',head)
    finally:source.close()
    store=Store(out/'derivations.sqlite3',create=True);store.close()
    proc=subprocess.run([sys.executable,str(BASE/'run.py'),'child',str(out),head],capture_output=True,text=True,timeout=15)
    if proc.returncode!=7 or proc.stdout:raise ValueError('unexpected_child_exit')
    store=Store(out/'derivations.sqlite3')
    try:
        result=store.get('repair-001');again=store.put('repair-001',snapshot,repair.propose(op['response']['content']))
        assert again==result and store.db.execute('SELECT COUNT(*) FROM derivations').fetchone()[0]==1
    finally:store.close()
    proc=subprocess.run([sys.executable,str(BASE/'run.py'),'read',str(out/'derivations.sqlite3'),result['digest']],capture_output=True,text=True,check=True,timeout=15)
    assert json.loads(proc.stdout)==result
    assert sha(original)==original_hash and sha(out/'source-copy.sqlite3')==copy_hash
    report=dict(status='complete',real_model_calls=0,derivations=1,derived_status=result['record']['assessment']['status'],derivation_digest=result['digest'],source_state='response_ready',source_files_unchanged=True,original_database_sha256=original_hash,copy_database_sha256=copy_hash,lost_ack_recovered=True,repeated_put_same_result=True,new_process_exact_recovery=True,admission='not_admitted')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
