"""Run only the frozen failed B slots under a separate versioned profile."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

from agora.evidence_answer_flow import ZaiProvider, _save, run_flow  # noqa: E402
from agora.qasper import sha  # noqa: E402
from verify import HERE, verify  # noqa: E402

FREEZE_PATH = HERE / 'correction-v2-freeze.json'
PROFILE_PATH = HERE / 'correction-v2-profile.json'
CODE_PATHS = (
    'experiments/evidence-answer-flow-t0-v1/run_failed_slots_v2.py',
    'src/agora/evidence.py',
    'src/agora/evidence_ids.py',
    'src/agora/evidence_answer_flow.py',
    'src/agora/split_review.py',
    'src/agora/coverage_cli.py',
    'src/agora/omission_cli.py',
)


def now():
    return datetime.now(timezone.utc).isoformat()


def preflight():
    verify()
    frozen = json.loads(FREEZE_PATH.read_text(encoding='utf-8'))
    profile = json.loads(PROFILE_PATH.read_text(encoding='utf-8'))
    if frozen['schema'] != 'agora/t0-failed-slots-correction/v2' or frozen['base_denominator'] != 6:
        raise ValueError('invalid_correction_freeze')
    if frozen['profile_sha256'] != sha(PROFILE_PATH.read_bytes()):
        raise ValueError('profile_hash_mismatch')
    actual_code = {name: sha((ROOT / name).read_bytes()) for name in CODE_PATHS}
    if frozen['implementation_sha256'] != actual_code:
        raise ValueError('implementation_hash_mismatch')
    base = ROOT / frozen['base_run']
    if sha((base / 'result.json').read_bytes()) != frozen['base_result_sha256']:
        raise ValueError('base_result_mismatch')
    prior = json.loads((base / 'result.json').read_text(encoding='utf-8'))
    cases = json.loads((HERE / 'freeze.json').read_text(encoding='utf-8'))['cases']
    cases_by_id = {case['id']: case for case in cases}
    rows = {row['id']: row for row in prior['pairs']}
    if (prior['status'] != 'complete_execution' or len(rows) != 6 or
            set(frozen['failed_slots']) != {'case-03', 'case-04', 'case-06'} or
            len(frozen['failed_slots']) != 3):
        raise ValueError('base_series_not_frozen')
    selected = []
    for name in frozen['failed_slots']:
        case, row = cases_by_id[name], rows[name]
        if row['arms']['B']['status'] not in ('incomplete', 'review_incomplete'):
            raise ValueError('not_a_failed_slot')
        source_path = base / name / 'source.txt'
        if sha(source_path.read_bytes()) != case['source_sha256']:
            raise ValueError('source_hash_mismatch')
        selected.append((case, source_path, row['arms']['B']['status']))
    return frozen, profile, selected, actual_code


def run(out, provider):
    frozen, profile, selected, code_hashes = preflight()
    out = Path(out)
    out.mkdir(mode=0o700, parents=False, exist_ok=False)
    result = {'schema': 'agora/t0-failed-slots-correction-run/v2',
              'status': 'running', 'started_at': now(),
              'correction_freeze_sha256': sha(FREEZE_PATH.read_bytes()),
              'profile_file_sha256': sha(PROFILE_PATH.read_bytes()),
              'implementation_sha256': code_hashes,
              'base_run': frozen['base_run'], 'base_denominator': 6,
              'selected_slots': [case['id'] for case, _, _ in selected],
              'model_requested': frozen['model_requested'],
              'model_effective': 'unknown', 'rows': [],
              'adjudication': 'not_performed', 'memory_admission': 'not_performed',
              'interpretation': 'separate_failed_slot_correction'}
    _save(out / 'result.json', result)
    for case, source_path, original_status in selected:
        start = time.monotonic()
        flow = run_flow(source_path, 'qasper:' + case['document_id'],
                        case['source_sha256'], case['question'], case['requirements'],
                        out / case['id'], provider, provider_id='zai',
                        model_requested=frozen['model_requested'],
                        diagnose_omissions=True, response_language='en', profile=profile)
        result['rows'].append({'id': case['id'], 'original_status': original_status,
                               'correction_status': flow['status'],
                               'dispatches': flow['dispatches'],
                               'elapsed_seconds': round(time.monotonic() - start, 3),
                               'result': case['id'] + '/result.json'})
        _save(out / 'result.json', result)
    result['status'] = 'complete_execution'
    result['ended_at'] = now()
    _save(out / 'result.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out', type=Path, help='New private run directory')
    args = parser.parse_args()
    output = run(args.out, ZaiProvider())
    print(json.dumps({'status': output['status'], 'slots': len(output['rows']),
                      'output': str(args.out / 'result.json')}))
