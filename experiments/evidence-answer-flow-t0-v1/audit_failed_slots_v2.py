"""Offline structural audit of the separate failed-slot correction."""

import argparse
from collections import Counter
import json
from pathlib import Path

from verify import HERE, ROOT, sha, verify


def audit(path):
    verify()
    frozen_path = HERE / 'correction-v2-freeze.json'
    frozen = json.loads(frozen_path.read_text(encoding='utf-8'))
    path = Path(path)
    result = json.loads((path / 'result.json').read_text(encoding='utf-8'))
    if (result['schema'] != 'agora/t0-failed-slots-correction-run/v2' or
            result['correction_freeze_sha256'] != sha(frozen_path.read_bytes()) or
            result['profile_file_sha256'] != frozen['profile_sha256'] or
            result['implementation_sha256'] != frozen['implementation_sha256'] or
            result['base_denominator'] != 6 or
            result['selected_slots'] != frozen['failed_slots'] or
            len(result['rows']) != 3):
        raise ValueError('correction_manifest_mismatch')
    if any(sha((ROOT / name).read_bytes()) != digest for name, digest in
           frozen['implementation_sha256'].items()):
        raise ValueError('implementation_hash_mismatch')
    if sha((ROOT / frozen['base_run'] / 'result.json').read_bytes()) != frozen['base_result_sha256']:
        raise ValueError('base_result_mismatch')
    profile = json.loads((HERE / 'correction-v2-profile.json').read_text(encoding='utf-8'))
    profile_digest = sha((json.dumps(profile, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')) + '\n').encode('utf-8'))
    cases = {case['id']: case for case in
             json.loads((HERE / 'freeze.json').read_text(encoding='utf-8'))['cases']}
    counts = Counter()
    models = Counter()
    dispatches = responses = tokens = 0
    rows = []
    for case_id, row in zip(frozen['failed_slots'], result['rows']):
        if case_id != row['id']:
            raise ValueError('slot_order_mismatch')
        case = cases[case_id]
        folder = path / case_id
        flow = json.loads((folder / 'result.json').read_text(encoding='utf-8'))
        if (flow['status'] != row['correction_status'] or
                flow['dispatches'] != row['dispatches'] or
                flow['source_sha256'] != case['source_sha256'] or
                flow.get('profile_sha256') != profile_digest or
                flow.get('profile') != profile):
            raise ValueError('flow_binding_mismatch')
        attempts = sorted(folder.glob('*-attempt.json'))
        receipts = sorted(folder.glob('*-response.json'))
        if len(attempts) != row['dispatches']:
            raise ValueError('attempt_count_mismatch')
        for ordinal, file in enumerate(attempts, 1):
            attempt = json.loads(file.read_text(encoding='utf-8'))
            if (attempt['ordinal'] != ordinal or
                    attempt['source_sha256'] != case['source_sha256'] or
                    attempt['model_requested'] != frozen['model_requested']):
                raise ValueError('attempt_binding_mismatch')
        for file in receipts:
            receipt = json.loads(file.read_text(encoding='utf-8'))
            models[receipt.get('reported_model') or 'unknown'] += 1
            tokens += (receipt.get('usage') or {}).get('total_tokens') or 0
        for stage in flow['stages'].values():
            if stage.get('path') and sha((folder / stage['path']).read_bytes()) != stage['sha256']:
                raise ValueError('stage_hash_mismatch')
        counts[row['correction_status']] += 1
        dispatches += len(attempts)
        responses += len(receipts)
        rows.append({'id': case_id, 'original_status': row['original_status'],
                     'correction_status': row['correction_status'],
                     'dispatches': len(attempts), 'responses': len(receipts)})
    return {'schema': 'agora/t0-failed-slots-correction-audit/v2',
            'run': path.name, 'status': result['status'], 'base_denominator': 6,
            'selected_slots': 3, 'statuses': dict(counts), 'dispatches': dispatches,
            'responses': responses, 'reported_total_tokens': tokens,
            'model_reported': dict(models), 'rows': rows,
            'adjudication': 'not_performed', 'original_t0_result': '3/6 unchanged'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.run), ensure_ascii=False, indent=2))
