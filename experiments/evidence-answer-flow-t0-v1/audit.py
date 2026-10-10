"""Offline structural audit of a frozen T0 run; no semantic adjudication."""

import argparse
from collections import Counter
import json
from pathlib import Path

from verify import HERE, sha, verify


def audit(path):
    verify()
    freeze = json.loads((HERE / 'freeze.json').read_text(encoding='utf-8'))
    path = Path(path)
    index = json.loads((path / 'result.json').read_text(encoding='utf-8'))
    if (index['freeze_sha256'] != sha((HERE / 'freeze.json').read_bytes()) or
            index['denominator'] != 6 or len(index['pairs']) != 6):
        raise ValueError('run_freeze_mismatch')
    report = {'run': path.name, 'execution_status': index['status'],
              'denominator': 6, 'pairs': [], 'arm_statuses': {'A': {}, 'B': {}},
              'dispatches': 0, 'responses': 0, 'reported_total_tokens': 0,
              'model_reported': {}, 'adjudication': 'not_performed'}
    counts = {'A': Counter(), 'B': Counter()}
    models = Counter()
    for case, pair in zip(freeze['cases'], index['pairs']):
        if case['id'] != pair['id'] or case['run_order'] != pair['order'] or set(pair['arms']) != {'A', 'B'}:
            raise ValueError('pair_identity_mismatch')
        source = (path / case['id'] / 'source.txt').read_bytes()
        if sha(source) != case['source_sha256']:
            raise ValueError('run_source_mismatch')
        row = {'id': case['id'], 'stratum': case['stratum'], 'order': pair['order'], 'arms': {}}
        for arm in ('A', 'B'):
            info = pair['arms'][arm]
            result = json.loads((path / info['result']).read_text(encoding='utf-8'))
            if info['status'] != result['status'] or info['dispatches'] != result['dispatches']:
                raise ValueError('arm_manifest_mismatch')
            folder = path / case['id'] / arm
            attempts = sorted(folder.glob('*-attempt.json'))
            responses = sorted(folder.glob('*-response.json'))
            if len(attempts) != info['dispatches']:
                raise ValueError('attempt_count_mismatch')
            for ordinal, attempt_path in enumerate(attempts, 1):
                attempt = json.loads(attempt_path.read_text(encoding='utf-8'))
                if (attempt['ordinal'] != ordinal or attempt['source_sha256'] !=
                        case['source_sha256'] or attempt['model_requested'] !=
                        freeze['comparison']['model_requested']):
                    raise ValueError('attempt_binding_mismatch')
            for response_path in responses:
                receipt = json.loads(response_path.read_text(encoding='utf-8'))
                model = receipt.get('reported_model') or 'unknown'
                models[model] += 1
                usage = receipt.get('usage') or {}
                report['reported_total_tokens'] += usage.get('total_tokens') or 0
            for stage in result.get('stages', {}).values():
                if stage.get('path') and sha((folder / stage['path']).read_bytes()) != stage['sha256']:
                    raise ValueError('stage_hash_mismatch')
            counts[arm][info['status']] += 1
            report['dispatches'] += len(attempts)
            report['responses'] += len(responses)
            row['arms'][arm] = {'status': info['status'], 'dispatches': len(attempts),
                                'responses': len(responses),
                                'elapsed_seconds': info['elapsed_seconds']}
        report['pairs'].append(row)
    report['arm_statuses'] = {arm: dict(c) for arm, c in counts.items()}
    report['model_reported'] = dict(models)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.run), ensure_ascii=False, indent=2))
