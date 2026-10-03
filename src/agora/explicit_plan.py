"""Reproducible caller-selected passage plans; selection is not verified coverage."""
import json
from .source import FileSourceAdapter, SourceError, integer, parse_range
from .passages import query_passages

VERSION = 'agora/explicit-passage-plan/v1'


def prepare(adapter, revision, question, ranges, budget=5000):
    if type(question) is not str or not question.strip() or len(question) > 2000:
        raise SourceError('invalid_question')
    question.encode('utf-8')
    integer(budget, 1, 4*1024*1024, 'invalid_content_budget')
    if type(ranges) is not list or not 1 <= len(ranges) <= 32:
        raise SourceError('invalid_reference_ranges')
    pairs = []
    for pair in ranges:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2 or any(type(n) is not int for n in pair):
            raise SourceError('invalid_reference_ranges')
        pairs.append(list(pair))
    envelope = adapter.fetch(revision, [tuple(p) for p in pairs], content_budget=budget)
    return dict(schema=VERSION, source_id=adapter.source_id, source_sha256=revision,
                question=question, ranges=pairs, budget_bytes=budget, envelope=envelope,
                selection_method='caller_selected_ranges', selection_verified=False,
                global_completeness='not_established', memory_admission='not_performed')


def generate(source, plan, plan_hash, question, provider, citation_mode):
    adapter = FileSourceAdapter(source, plan['source_id'])
    if question != plan['question']:
        raise ValueError('plan_question_mismatch')
    rebuilt = prepare(adapter, plan['source_sha256'], question, plan['ranges'], plan['budget_bytes'])
    if rebuilt != plan:
        raise ValueError('plan_reproduction_mismatch')
    result = query_passages(adapter, plan['source_sha256'], question, provider, 'reference',
                            ranges=[tuple(p) for p in plan['ranges']], content_budget=plan['budget_bytes'],
                            prompt_budget=65536, citation_mode=citation_mode, scope_guard=True)
    result.update(plan_sha256=plan_hash, plan_schema=VERSION,
                  selection_method='caller_selected_ranges', selection_verified=False,
                  global_completeness='not_established', reading_budget_bytes=plan['budget_bytes'],
                  expansion_policy='explicit_review_and_budget_required')
    return result


def add_command(sub):
    p = sub.add_parser('plan-passages', help='Fijar selección explícita de pasajes; no recuperación automática ni proveedor.')
    for name in ('source', 'source-id', 'source-sha256', 'question', 'out'):
        p.add_argument('--'+name, required=True)
    p.add_argument('--range', type=parse_range, action='append', required=True)
    p.add_argument('--budget', type=int, default=5000)


def run(args, write_new):
    plan = prepare(FileSourceAdapter(args.source, args.source_id), args.source_sha256,
                   args.question, args.range, args.budget)
    write_new(args.out, plan)
    return dict(status='prepared', schema=VERSION, output=str(args.out), provider_calls=0,
                delivered_bytes=plan['envelope']['delivered_bytes'], selection_verified=False)
