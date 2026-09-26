"""Read-only integrity audit; never retries requests or infers model accuracy."""
import hashlib
import json
from pathlib import Path
import sys


def audit(directory):
    root = Path(directory)
    load = lambda name: json.loads((root/name).read_text())
    digest = lambda name: hashlib.sha256((root/name).read_bytes()).hexdigest()
    frozen = load('freeze.json')
    if not all(digest(name) == value for name, value in frozen.items()):
        raise ValueError('frozen_file_changed')
    calls, rows = load('calls.json'), load('scores.json')
    if len(calls) > 18 or len(rows) > 12:
        raise ValueError('budget_exceeded')
    for call in calls:
        ordinal = call['ordinal']
        if digest('request-%02d.json' % ordinal) != call['request_sha256']:
            raise ValueError('request_changed')
        if 'response_sha256' in call and digest('response-%02d.json' % ordinal) != call['response_sha256']:
            raise ValueError('response_changed')
    for row in rows:
        if digest(row['case']+'-'+row['mode']+'.json') != row['result_sha256']:
            raise ValueError('result_changed')
    return {'integrity':'verified', 'calls':len(calls),
            'complete_arms':sum(row['status']=='complete' for row in rows),
            'unknown_usage_calls':sum('tokens' not in call for call in calls)}

if __name__ == '__main__':
    print(json.dumps(audit(sys.argv[1])))
