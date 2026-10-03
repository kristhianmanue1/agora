#!/usr/bin/env python3
"""Explicit offline relation candidate tooling; emits JSON to stdout."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from agora.relation_candidates import evidence, template, validate
from agora.transform import unique_object


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['units', 'template', 'validate'])
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--source-id', required=True)
    parser.add_argument('--candidate', type=Path)
    args = parser.parse_args()
    if (args.action == 'validate') != (args.candidate is not None):
        parser.error('--candidate is required only for validate')
    try:
        with args.source.open('rb') as stream:
            raw = stream.read(4 * 1024 * 1024 + 1)
        if args.action == 'units':
            result = evidence(raw, args.source_id)
        elif args.action == 'template':
            result = template(raw, args.source_id)
        else:
            with args.candidate.open('rb') as stream:
                content = stream.read(1024 * 1024 + 1)
            if len(content) > 1024 * 1024:
                raise ValueError('candidate_too_large')
            result = validate(raw, args.source_id, json.loads(content, object_pairs_hook=unique_object))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(json.dumps({'status': 'rejected', 'error': str(exc)}), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
