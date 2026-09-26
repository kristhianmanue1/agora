"""Explicit GLM transport for the experimental multi-passage consumer."""
import argparse
import json
import os
from pathlib import Path
import urllib.request
from .__main__ import ENDPOINT, token_limit, timeout_limit
from .source import FileSourceAdapter, digest, parse_range
from .passages import query_passages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--source-id', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--question', required=True)
    parser.add_argument('--mode', choices=['source', 'reference', 'retrieve'], required=True)
    parser.add_argument('--range', type=parse_range, action='append')
    parser.add_argument('--content-budget', type=int, default=2048)
    parser.add_argument('--prompt-budget', type=int, default=65536)
    parser.add_argument('--top-k', type=int, default=3)
    parser.add_argument('--fallback-source-budget', type=int, help='Opt in: full source only on zero lexical matches, bounded bytes')
    parser.add_argument('--model', required=True)
    parser.add_argument('--max-output-tokens', type=token_limit, default=2048)
    parser.add_argument('--timeout-seconds', type=timeout_limit, default=90)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    attempts = 0
    modules = ("passages.py", "passage_cli.py", "source.py", "query.py", "transform.py", "__main__.py")
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

    options = {'content_budget': args.content_budget, 'prompt_budget': args.prompt_budget,
               'top_k': args.top_k}
    if args.fallback_source_budget is not None:
        options['fallback_source_budget'] = args.fallback_source_budget
    if args.range is not None:
        options['ranges'] = args.range
    try:
        adapter = FileSourceAdapter(args.source, args.source_id)
        result = query_passages(adapter, args.sha256, args.question, provider, args.mode, **options)
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
