"""Repeatable local demonstration. Uses synthetic text and no model calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source = args.out / 'synthetic.txt'
    first = 'Inicio: prohibido publicar datos reales.\r\n'.encode()
    last = 'Final: permiso sólo para datos ficticios.\n'.encode()
    data = first + ('Contexto sintético á 😀 sin decisión adicional.\n' * 45000).encode() + last
    source.write_bytes(data)
    revision = sha(data)
    root = Path(__file__).resolve().parents[2]
    env = dict(os.environ, PYTHONPATH=str(root / 'src'), PYTHONDONTWRITEBYTECODE='1')
    outcomes = []

    def call(name, action, *options):
        output = args.out / (name + '.json')
        command = [sys.executable, '-m', 'agora.source', action,
                   '--source', str(source), '--source-id', 'synthetic-large-v1',
                   '--sha256', revision, '--out', str(output), *options]
        result = subprocess.run(command, env=env, text=True, capture_output=True)
        outcomes.append({'case': name, 'exit_code': result.returncode,
                         'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()})
        return result, output

    p, inv = call('inventory', 'inventory')
    assert p.returncode == 0, p.stderr
    inventory = json.loads(inv.read_bytes())
    units = inventory['units']
    position = 0
    for unit in units:
        assert unit['start_byte'] == position
        raw = data[position:unit['end_byte']]
        raw.decode('utf-8')
        assert sha(raw) == unit['sha256']
        position = unit['end_byte']
    assert position == len(data)
    ranges = ['--range', f'0:{len(first)}', '--range', f'{len(data)-len(last)}:{len(data)}']
    p, fetched = call('distant', 'fetch', *ranges, '--content-budget', '128', '--envelope-budget', '4096')
    assert p.returncode == 0, p.stderr
    envelope = json.loads(fetched.read_bytes())
    assert [s['text'].encode() for s in envelope['spans']] == [first, last]
    assert envelope['coverage'] == 'partial'
    assert envelope['evidence_sufficiency'] == 'unknown'
    p, rejected = call('budget-rejected', 'fetch', *ranges, '--content-budget', '1')
    assert p.returncode == 2 and 'content_budget_exceeded' in p.stderr and not rejected.exists()
    source.write_bytes(data.replace(b'Inicio', b'Cambio', 1))
    p, rejected = call('revision-rejected', 'fetch', *ranges)
    assert p.returncode == 2 and 'source_revision_mismatch' in p.stderr and not rejected.exists()
    source.write_bytes(data)
    report = {'schema': 'agora/file-source-pilot/v0.1', 'synthetic': True,
              'source_bytes': len(data), 'source_sha256': revision, 'units': len(units),
              'delivered_bytes': envelope['delivered_bytes'], 'envelope_bytes': fetched.stat().st_size,
              'model_calls': 0, 'memory_writes': 0, 'outcomes': outcomes,
              'limits': 'Transport only; no search, generation, semantic validation or token savings claim.',
              'implementation_sha256': sha((root / 'src/agora/source.py').read_bytes()),
              'pilot_sha256': sha(Path(__file__).read_bytes())}
    (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'outcomes'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
