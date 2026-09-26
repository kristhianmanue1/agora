"""Bounded API format capability probe; synthetic data, no tools or retries."""
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

ENDPOINT = 'https://api.z.ai/api/coding/paas/v4/chat/completions'
SCHEMA = {'type': 'object', 'properties': {'marker': {'type': 'string', 'enum': ['schema_ok']}, 'quotes': {'type': 'array', 'items': {'type': 'string'}}}, 'required': ['marker', 'quotes'], 'additionalProperties': False}
STRICT = {'type': 'json_schema', 'json_schema': {'name': 'format_probe', 'strict': True, 'schema': SCHEMA}}
CASES = [
    ('json_positive', {'type': 'json_object'}, 'Return only this JSON object: {"marker":"schema_ok","quotes":[]}'),
    ('json_counterexample', {'type': 'json_object'}, 'Return only this JSON object: {"marker":"prompt_value"}'),
    ('schema_counterexample', STRICT, 'Return only this JSON object: {"marker":"prompt_value"}'),
    ('schema_positive', STRICT, 'Return only this JSON object: {"marker":"schema_ok","quotes":[]}'),
]

def valid(value):
    return isinstance(value, dict) and set(value) == {'marker', 'quotes'} and value['marker'] == 'schema_ok' and isinstance(value['quotes'], list) and all(isinstance(x, str) for x in value['quotes'])

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def main():
    key = os.environ['ZAI_API_KEY']
    out = Path(__file__).resolve().parent / 'runs/probe-01'
    out.mkdir(parents=True, exist_ok=False)
    protocol = {'endpoint': ENDPOINT, 'model': 'glm-5.3-flash', 'temperature': 0, 'max_tokens': 2048, 'socket_timeout': 45, 'max_calls': 4, 'retries': 0, 'schema': SCHEMA, 'cases': CASES, 'claim': 'HTTP acceptance is not schema enforcement; one completed violation falsifies strict compliance for this request.', 'stop': 'access, rate limit, server, transport failure; a schema parameter rejection skips remaining schema case', 'limitations': 'Synthetic capability probe, not fidelity or QASPER evaluation.'}
    (out / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    (out / 'run.py').write_bytes(Path(__file__).read_bytes())
    manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}
    (out / 'freeze.json').write_text(json.dumps(manifest, indent=2) + '\n')
    rows = []
    for name, response_format, prompt in CASES:
        payload = {'model': protocol['model'], 'temperature': 0, 'max_tokens': 2048, 'messages': [{'role': 'user', 'content': prompt}], 'response_format': response_format}
        row = {'case': name, 'observed_at': datetime.now(timezone.utc).isoformat(), 'request': payload}
        start = time.monotonic()
        stop = False
        try:
            request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key})
            with urllib.request.build_opener(NoRedirect()).open(request, timeout=45) as response:
                raw = response.read(1048577)
                row['http_status'] = response.status
            if len(raw) > 1048576:
                raise ValueError('response_too_large')
            data = json.loads(raw)
            choice = data['choices'][0]
            row.update(content=choice['message'].get('content'), finish_reason=choice.get('finish_reason'), reported_model=data.get('model'), response_id=data.get('id'), usage=data.get('usage'))
            try:
                parsed = json.loads(row['content'])
                row.update(json_valid=True, schema_valid=valid(parsed))
            except (ValueError, TypeError):
                row.update(json_valid=False, schema_valid=False)
        except urllib.error.HTTPError as exc:
            row.update(http_status=exc.code, error='HTTPError')
            stop = True
        except Exception as exc:
            row['error'] = type(exc).__name__
            stop = True
        row['seconds'] = round(time.monotonic() - start, 3)
        if key in json.dumps(row):
            row = {'case': name, 'error': 'sensitive_response_rejected'}
            stop = True
        rows.append(row)
        (out / 'results.json').write_text(json.dumps(rows, indent=2) + '\n')
        print(json.dumps({k: v for k, v in row.items() if k not in ('request',)}), flush=True)
        if stop:
            break
    assert all(hashlib.sha256((out / n).read_bytes()).hexdigest() == h for n, h in manifest.items())
    (out / 'integrity.json').write_text(json.dumps({'frozen_files_verified': True, 'results_sha256': hashlib.sha256((out / 'results.json').read_bytes()).hexdigest()}) + '\n')

if __name__ == '__main__':
    main()
