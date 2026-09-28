"""Offline backup/restart demonstration; zero model calls."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from store import Store,protocol,encode,VALIDATOR_MANIFEST
BASE=Path(__file__).resolve().parent

def main():
    if sys.argv[1]=='read':
        store=Store(sys.argv[2])
        try:print(encode({issue:store.history(issue,head) for issue,head in json.loads(sys.argv[3]).items()}))
        finally:store.close()
        return
    os.umask(0o077)
    out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
    cases=json.loads((BASE.parent/'open-issues-v4/replay-fixtures.json').read_text())
    store=Store(out/'issues.sqlite3',create=True);heads={};expected={}
    try:
        for case in cases:
            candidate=encode(protocol.prepare_candidate(case['original_content'],case['input']))
            heads[case['name']]=store.append(case['name'],None,case['input'],case['original_content'],candidate,dict(kind='offline_replay',original_content_sha256=case['original_content_sha256']))
            expected[case['name']]=store.history(case['name'],heads[case['name']])
        backup=sqlite3.connect(out/'backup.sqlite3')
        try:store.db.backup(backup)
        finally:backup.close()
    finally:store.close()
    # The child receives only a backup path and external expected heads.
    proc=subprocess.run([sys.executable,str(BASE/'run.py'),'read',str(out/'backup.sqlite3'),encode(heads)],capture_output=True,text=True,check=True,timeout=15)
    actual=json.loads(proc.stdout)
    if actual!=expected:raise ValueError('restart_mismatch')
    report=dict(status='complete',real_model_calls=0,independent_process=True,backup_exact_recovery=True,sidecars_read_by_child=False,heads=heads,validator_manifest=VALIDATOR_MANIFEST,states={k:v[-1]['record']['assessment']['status'] for k,v in actual.items()},original_model_content_preserved=all(actual[c['name']][-1]['record']['model_content']==c['original_content'] for c in cases),admission='not_admitted')
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report))
if __name__=='__main__':main()
