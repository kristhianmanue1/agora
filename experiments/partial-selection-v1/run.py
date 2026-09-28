"""Two bounded GLM evaluations of progressively expanded synthetic evidence."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    os.umask(0o077)
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    recovery = load('partial_recovery', BASE.parent/'issue-recovery-v1/recovery.py')
    envelope = load('partial_envelope', BASE.parent/'skopos-issue-bridge-v2/envelope.py')
    fixtures = load('partial_fixtures', BASE.parent/'issue-flow-v1/fixtures.py')
    skopos = ROOT.parent/'skopos/experiments/meeting-source-v1'
    pilot = load('partial_pilot', skopos/'pilot.py')
    export = load('partial_export', skopos/'export.py')
    system = recovery.storage.protocol.SYSTEM + '\n' + envelope.POLICY
    # Isolated module configuration: bind the actual system text to request identity.
    recovery.CONFIG = dict(recovery.CONFIG, system_text=system, system_sha256=hashlib.sha256(system.encode()).hexdigest())
    source = dict(source_id='meeting-partial-synthetic', revision=1, supersedes=None, complete=False, segments=[
        dict(id='owner', start_ms=1000, end_ms=9000, speaker='Coordinación sintética', text='Responsabilidad: Lina sigue siendo responsable de Nube.'),
        dict(id='date', start_ms=10000, end_ms=19000, speaker='Coordinación sintética', text='Calendario: Nube se entrega el 2026-10-21.')])
    save(out/'meeting.json', source)
    producer = pilot.MeetingStore()
    producer.ingest(out/'meeting.json')
    packets = [export.export_packet(producer, terms) for terms in (['Responsabilidad'], ['Responsabilidad', 'Calendario'])]
    assert '2026-10-21' not in packets[0]['text'] and '2026-10-21' in packets[1]['text']
    assert packets[0]['source_sha256'] == packets[1]['source_sha256']
    save(out/'expectations.json', dict(partial=dict(status='partial', date=None, owner='Lina'), expanded=dict(status='resolved', date='2026-10-21', owner='Lina'), semantic_review='Partial reason must limit absence to available selection; expanded packets are one origin, not independent corroboration.', max_calls=2, max_output_tokens_per_call=8192, http_timeout=180, retries=0))
    paths = [Path(__file__).resolve(), BASE/'README.md', BASE.parent/'issue-recovery-v1/recovery.py', BASE.parent/'issue-recovery-v1/store.py', BASE.parent/'issue-flow-v1/adapter.py', BASE.parent/'issue-flow-v1/fixtures.py', BASE.parent/'issue-store-v1/store.py', BASE.parent/'open-issues-v3/protocol.py', BASE.parent/'skopos-issue-bridge-v2/envelope.py', BASE.parent/'skopos-issue-bridge-v1/bridge.py', BASE.parent/'review-invariance-v1/transport_diagnostic.py', skopos/'pilot.py', skopos/'export.py']
    frozen = {str(p):sha(p) for p in paths}
    save(out/'freeze.json', frozen)
    store = recovery.Store(out/'issues.sqlite3', create=True)
    data, raw, _ = fixtures.inputs()
    head = store.append('nube', None, data, raw, {'kind':'manual_fixture'})
    report = dict(status='prepared', calls=0, stages=[], known_tokens=0)
    save(out/'report.json', report)
    try:
        for index, packet in enumerate(packets):
            stage = out/str(index+1)
            stage.mkdir()
            save(stage/'packet.json', packet)
            incoming, _ = envelope.create(packet, '2026-10-08', producer.fetch)
            prepared = recovery.flow.prepare(store, 'nube', head, incoming, '2026-10-08')
            save(stage/'prepared.json', prepared)
            def provider(base_system, user):
                assert base_system == recovery.storage.protocol.SYSTEM
                if any(sha(Path(p)) != value for p,value in frozen.items()):
                    raise ValueError('code_changed_since_freeze')
                request = dict(model='glm-5.3-flash', temperature=0, max_tokens=8192, response_format={'type':'json_object'}, messages=[dict(role='system',content=system),dict(role='user',content=user)])
                save(stage/'request.json', request)
                report['calls'] += 1
                report['status'] = 'attempted'
                save(out/'report.json', report)
                start = time.monotonic()
                try:
                    proc = subprocess.run([sys.executable,str(BASE.parent/'review-invariance-v1/transport_diagnostic.py'),str(stage/'request.json'),'180'], capture_output=True,text=True,timeout=190)
                    response = json.loads(proc.stdout)
                    save(stage/'response.json', response)
                    if proc.returncode: raise ValueError('transport_failed')
                    usage = (response.get('usage') or {}).get('total_tokens')
                    if type(usage) is int: report['known_tokens'] += usage
                    return response
                finally:
                    report['last_call_seconds'] = round(time.monotonic()-start,3)
                    save(out/'report.json', report)
            result = recovery.evaluate(store, 'partial-selection-'+str(index+1), prepared, provider)
            save(stage/'candidate.json', result)
            assessment = result['assessment']
            expected = {'date':None if index == 0 else '2026-10-21','owner':'Lina'}
            matched = assessment['status'] == ('partial' if index == 0 else 'resolved') and {k:v['observed_value'] for k,v in assessment['fields'].items()} == expected
            report['stages'].append(dict(stage=index+1,expected_values_match=matched,result=result,seconds=report['last_call_seconds']))
            save(out/'report.json', report)
            if not matched: raise ValueError('semantic_values_mismatch')
            head = result['revision_sha256']
        store.close()
        store = recovery.Store(out/'issues.sqlite3')
        history = store.history('nube', head)
        assert len(history) == 3
        recovered_packets = [envelope.recover(s) for s in history[-1]['record']['input']['sources'][1:]]
        assert recovered_packets == packets
        for index in (1,2):
            op = recovery.inspect(store, 'partial-selection-'+str(index))
            assert op['request']['provider']['system_text'] == system
        report.update(status='complete',revisions=3,packets_recovered=True,system_bound_in_operation=True,semantic_reason_review='pending producer review; schema and value checks alone do not establish faithfulness')
    except Exception as exc:
        report.update(status='failed',failure=type(exc).__name__,detail=str(exc)[:160] if isinstance(exc,ValueError) else 'execution_failed',retry='none')
    finally:
        store.close()
        save(out/'report.json', report)
        print(json.dumps(report,ensure_ascii=False))
    return 0 if report['status']=='complete' else 2
if __name__ == '__main__':
    raise SystemExit(main())
