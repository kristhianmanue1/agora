"""Explicit GLM transport for the experimental traversal query consumer."""
import argparse
import json
import os
from pathlib import Path
import urllib.request
from .__main__ import ENDPOINT, token_limit, timeout_limit
from .source import FileSourceAdapter, digest, parse_range
from .traversal_query import query_traversal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--source-id', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--question', required=True)
    parser.add_argument('--traversal', type=Path, required=True)
    parser.add_argument('--traversal-sha256', required=True)
    parser.add_argument('--prompt-budget', type=int, default=65536)
    parser.add_argument('--model', required=True)
    parser.add_argument('--max-output-tokens', type=token_limit, default=2048)
    parser.add_argument('--timeout-seconds', type=timeout_limit, default=90)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    attempts = 0
    modules = ("passages.py", "traversal_cli.py", "traversal_query.py", "traversal.py", "source.py", "query.py", "transform.py", "__main__.py")
    initial_hashes = {name: digest(Path(__file__).with_name(name).read_bytes()) for name in modules}

    def provider(system, user):
        nonlocal attempts
        if attempts:
            raise RuntimeError('request_budget_exceeded')
        key = os.environ.get('ZAI_API_KEY')
        if not key:
            raise RuntimeError('provider_key_missing')
        payload = {'model': args.model, 'messages': [{'role': 'system', 'content': system},
                   {'role': 'user', 'content': user}], 'max_tokens': args.max_output_tokens,
                   'temperature': 0}
        request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(),
                  headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key})
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None
        attempts += 1
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=args.timeout_seconds) as response:
            raw = response.read(1048577)
        if len(raw) > 1048576:
            raise RuntimeError('provider_response_too_large')
        data = json.loads(raw)
        choice = data['choices'][0]
        receipt = {'content': choice['message']['content'], 'finish_reason': choice.get('finish_reason'),
                   'requested_model': args.model, 'reported_model': data.get('model'),
                   'response_id': data.get('id'), 'usage': data.get('usage')}
        if key in json.dumps(receipt):
            raise RuntimeError('sensitive_response_rejected')
        return receipt

    try:
        adapter = FileSourceAdapter(args.source, args.source_id)
        with args.traversal.open('rb') as stream:
            record_data = stream.read(8388609)
        result = query_traversal(adapter, args.sha256, args.question, record_data,
                                 args.traversal_sha256, provider, prompt_budget=args.prompt_budget)
    except Exception as exc:
        result = {'execution_status': 'failed', 'diagnostic': type(exc).__name__}
    result['http_attempts'] = attempts
    result['request_config'] = {'model': args.model, 'max_output_tokens': args.max_output_tokens,
                                'timeout_seconds': args.timeout_seconds, 'max_calls': 1, 'temperature': 0}
    result['implementation_hashes'] = initial_hashes
    final_hashes = {name: digest(Path(__file__).with_name(name).read_bytes()) for name in modules}
    result['implementation_unchanged'] = initial_hashes == final_hashes
    if initial_hashes != final_hashes:
        result.update(execution_status='rejected', diagnostic='implementation_changed_during_run')
    (args.out / 'result.json').write_text(json.dumps(result, ensure_ascii=True, indent=2) + '\n')
    print(json.dumps({k: result.get(k) for k in ('execution_status', 'answer_status', 'http_attempts')}))
    return 0 if result['execution_status'] == 'complete' else 2


if __name__ == '__main__':
    raise SystemExit(main())
