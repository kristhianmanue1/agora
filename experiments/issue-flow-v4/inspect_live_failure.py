"""Read retained invalid response and attempt local finalize only; never call LLM."""
import json
from pathlib import Path
import sys
import recovery

def forbidden(request):raise AssertionError('unexpected_provider_call')
def main():
    out=Path(sys.argv[1]).resolve();store=recovery.Store(out/'issues.sqlite3')
    try:
        before=recovery.inspect(store,'live-v4-001')
        original=json.loads((out/'response.json').read_text())
        assert before['state']=='response_ready' and before['response']==original
        prepared=json.loads((out/'prepared.json').read_text())
        try:
            recovery.evaluate(store,'live-v4-001',prepared,forbidden)
            raise AssertionError('invalid_response_accepted')
        except json.JSONDecodeError as exc:
            error=dict(type=type(exc).__name__,message=exc.msg)
        after=recovery.inspect(store,'live-v4-001')
        history=store.history('nube',prepared['package']['expected_head'])
        assert before==after and len(history)==1
        print(json.dumps(dict(status='complete',retained_response_exact=True,operation_unchanged=True,operation_state=after['state'],revisions=1,no_provider_call=True,validation_error=error)))
    finally:store.close()
if __name__=='__main__':main()
