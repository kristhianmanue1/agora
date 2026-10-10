"""Execute a new frozen T0 AB/BA calibration run; never resume or retry."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

from agora.evidence_answer_flow import Dispatch, ZaiProvider, _save  # noqa: E402
from agora.evidence_answer_flow import run_flow  # noqa: E402
from agora.qasper import render, sha  # noqa: E402
from agora.source import FileSourceAdapter  # noqa: E402
from agora.transform import unique_object  # noqa: E402
from verify import verify, HERE  # noqa: E402


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def baseline(source_path, case, prompt, out, provider, model):
    out.mkdir(mode=0o700, exist_ok=False)
    adapter = FileSourceAdapter(source_path, 'qasper:' + case['document_id'], 160000)
    source = adapter._read(case['source_sha256']).decode('utf-8')
    user = prompt['user_template']
    for key, value in {
        'source_id': adapter.source_id,
        'source_sha256': case['source_sha256'],
        'question': case['question'],
        'requirements_json': json.dumps(case['requirements'], ensure_ascii=False),
        'source_text': source,
    }.items():
        user = user.replace('{{' + key + '}}', value)
    if '{{' in user:
        raise ValueError('unresolved_baseline_placeholder')
    dispatch = Dispatch(out, adapter, case['source_sha256'], provider, 'zai', model)
    result = {'schema': 'agora/t0-baseline-run/v1', 'status': 'attempted',
              'source_sha256': case['source_sha256'], 'question': case['question'],
              'requirements': case['requirements'], 'model_requested': model,
              'model_effective': 'unknown', 'started_at': utc_now(),
              'dispatches': 0, 'adjudication': 'not_performed'}
    start = time.monotonic()
    try:
        response = dispatch.call('baseline', prompt['system'], user,
                                 max_output_tokens=4096, timeout_seconds=120)
        result['response'] = response
        if response.get('finish_reason') != 'stop':
            raise ValueError('generation_incomplete')
        value = json.loads(response['content'], object_pairs_hook=unique_object)
        if type(value) is not dict or set(value) != {'status', 'claims', 'missing'}:
            raise ValueError('invalid_baseline_shape')
        if value['status'] not in ('answered', 'insufficient') or type(value['claims']) is not list:
            raise ValueError('invalid_baseline_status')
        if (type(value['missing']) is not str and
                (type(value['missing']) is not list or
                 any(type(item) is not str for item in value['missing']))):
            raise ValueError('invalid_baseline_missing')
        if value['status'] == 'insufficient' and value['claims']:
            raise ValueError('invalid_baseline_abstention')
        if any(type(claim) is not dict or set(claim) != {'text', 'quote'} or
               type(claim['text']) is not str or not claim['text'].strip() or
               type(claim['quote']) is not str or not claim['quote'] or
               claim['quote'] not in source for claim in value['claims']):
            raise ValueError('invalid_baseline_quote')
        result['answer'] = value
        result['status'] = 'candidate'
    except Exception as exc:
        result['status'] = 'remote_outcome_unknown' if dispatch.uncertain else 'invalid_or_incomplete'
        result['diagnostic'] = type(exc).__name__
    finally:
        result['dispatches'] = dispatch.count
        result['elapsed_seconds'] = round(time.monotonic() - start, 3)
        result['ended_at'] = utc_now()
        _save(out / 'result.json', result)
    return result


def run(out, provider):
    verified = verify()
    freeze = json.loads((HERE / 'freeze.json').read_text(encoding='utf-8'))
    prompt = json.loads((HERE / 'baseline-prompt.json').read_text(encoding='utf-8'))
    dataset = json.loads((ROOT / freeze['dataset']['path']).read_text(encoding='utf-8'))
    model = freeze['comparison']['model_requested']
    # Reconstruct and verify all six sources before any network call.
    prepared = []
    for case in freeze['cases']:
        source, _ = render(dataset[case['document_id']])
        if sha(source) != case['source_sha256']:
            raise ValueError('source_freeze_mismatch')
        prepared.append((case, source))
    out = Path(out)
    out.mkdir(mode=0o700, parents=False, exist_ok=False)
    index = {'schema': 'agora/t0-calibration-run/v1', 'status': 'running',
             'started_at': utc_now(), 'freeze_sha256': sha((HERE / 'freeze.json').read_bytes()),
             'verified': verified, 'model_requested': model,
             'model_effective': 'unknown', 'pairs': [], 'denominator': 6,
             'adjudication': 'not_performed', 'memory_admission': 'not_performed'}
    _save(out / 'result.json', index)
    for case, source in prepared:
        case_dir = out / case['id']
        case_dir.mkdir(mode=0o700)
        source_path = case_dir / 'source.txt'
        source_path.write_bytes(source)
        row = {'id': case['id'], 'stratum': case['stratum'],
               'order': case['run_order'], 'arms': {}}
        index['pairs'].append(row)
        _save(out / 'result.json', index)
        for arm in case['run_order']:
            started = time.monotonic()
            if arm == 'A':
                result = baseline(source_path, case, prompt, case_dir / 'A', provider, model)
            else:
                result = run_flow(source_path, 'qasper:' + case['document_id'],
                                  case['source_sha256'], case['question'],
                                  case['requirements'], case_dir / 'B', provider,
                                  provider_id='zai', model_requested=model,
                                  diagnose_omissions=True, response_language='en')
            row['arms'][arm] = {'status': result['status'],
                                'dispatches': result['dispatches'],
                                'elapsed_seconds': round(time.monotonic() - started, 3),
                                'result': f"{case['id']}/{arm}/result.json"}
            _save(out / 'result.json', index)
    index['status'] = 'complete_execution'
    index['ended_at'] = utc_now()
    _save(out / 'result.json', index)
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out', type=Path, help='New private run directory')
    args = parser.parse_args()
    result = run(args.out, ZaiProvider())
    print(json.dumps({'status': result['status'], 'pairs': len(result['pairs']),
                      'output': str(args.out / 'result.json')}))


if __name__ == '__main__':
    main()
