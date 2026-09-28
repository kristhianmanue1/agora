"""Lost acknowledgement after commit; restart must not invoke evaluator twice."""
import json
import os
from pathlib import Path
import subprocess
import sys
import recovery
from fixtures import seed,provider
BASE=Path(__file__).resolve().parent

def main():
    if sys.argv[1]=='child':
        out=Path(sys.argv[2]);store=recovery.Store(out/'issues.sqlite3')
        prepared=json.loads((out/'prepared.json').read_text())
        def counted(request):
            with (out/'provider-calls.txt').open('a') as f:f.write('simulated\n')
            return provider(request)
        try:recovery.evaluate(store,'arrival-001',prepared,counted)
        finally:store.close()
        raise SystemExit(7)  # Committed but caller receives no result.
    os.umask(0o077);out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
    store=recovery.Store(out/'issues.sqlite3',create=True)
    head,source=seed(store);prepared=recovery.flow.prepare(store,'nube',head,source,'2026-10-09')
    original=store.history('nube',head)[0];store.close()
    (out/'prepared.json').write_text(recovery.encode(prepared))
    proc=subprocess.run([sys.executable,str(BASE/'run.py'),'child',str(out)],capture_output=True,text=True,timeout=15)
    if proc.returncode!=7 or proc.stdout:raise ValueError('unexpected_child_outcome')
    store=recovery.Store(out/'issues.sqlite3')
    def forbidden(request):raise AssertionError('duplicate_provider_call')
    try:
        result=recovery.evaluate(store,'arrival-001',prepared,forbidden)
        history=store.history('nube',result['revision_sha256'])
        assert len(history)==2 and history[0]==original
        assert history[0]['record']['assessment']['status']=='partial' and result['assessment']['status']=='resolved'
        assert len(result['assessment']['reviewed_scope']['sources'])==2
        op=recovery.inspect(store,'arrival-001')
        assert op['request']['provider']['messages'][0]['content']==recovery.SYSTEM
    finally:store.close()
    assert (out/'provider-calls.txt').read_text()=='simulated\n'
    report=dict(status='complete',real_model_calls=0,simulated_provider_calls=1,lost_ack_recovered=True,child_exit=7,original_revision_preserved=True,revisions=2,scope_sources=2,operation_state=op['state'],result=result)
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
