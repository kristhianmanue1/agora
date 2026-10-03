"""Offline integrity and accounting checks; never certify semantic correctness."""
import hashlib
import json
from pathlib import Path
import sys


def verify_files(root, records):
    root = Path(root).resolve()
    seen = set()
    for record in records:
        path = (root / record['path']).resolve()
        if not path.is_relative_to(root) or record['path'] in seen:
            raise ValueError('invalid_or_duplicate_artifact_path')
        seen.add(record['path'])
        if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('artifact_hash_mismatch: ' + record['path'])


def accounting(answers, usage, labels):
    ids = [row['id'] for row in answers]
    if len(ids) != len(set(ids)) or set(ids) != set(labels):
        raise ValueError('case_denominator_mismatch')
    calls = [row['file'] for row in usage]
    if len(calls) != len(set(calls)):
        raise ValueError('duplicate_call_record')
    memos = 0
    response_ids = set()
    for row in usage:
        subtotal = 0
        for event in row['usage_events']:
            if not event.get('id') or event['id'] in response_ids:
                raise ValueError('missing_or_duplicate_provider_receipt')
            response_ids.add(event['id'])
            token_count = event['usage']['total_tokens']
            if type(token_count) is not int or token_count < 0:
                raise ValueError('invalid_token_count')
            subtotal += token_count
        if subtotal != row['reported_total_tokens']:
            raise ValueError('usage_subtotal_mismatch')
        memos += subtotal
    return dict(cases=len(ids), memos_http_records=len(calls),
                memos_observed_tokens=memos,
                agora_observed_tokens=sum(r['agora_usage']['total_tokens'] for r in answers),
                agora_rejected=sum(r['agora_status']=='rejected' for r in answers))


def verify(root):
    root = Path(root)
    manifest = json.loads((root/'experiments/benchmark-bank-v1/manifest.json').read_text())
    if manifest.get('schema') != 'aria/benchmark-evidence-bank/v1':
        raise ValueError('unsupported_bank_schema')
    verify_files(root, manifest['artifacts'])
    base = root/'experiments/memos-long-reserved-v1'
    read = lambda name: json.loads((base/name).read_text())
    result = accounting(read('comparison.json'), read('memos-usage.json'), read('assessment.json')['labels'])
    if result != manifest['expected_accounting']:
        raise ValueError('accounting_mismatch')
    return dict(status='verified', accounting=result, semantic_validity='not_certified',
                live_services_tested=False, external_costs='not_measured')


if __name__ == '__main__':
    try:
        print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status':'failed','diagnostic':str(exc)}))
        sys.exit(2)
