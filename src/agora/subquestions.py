"""Explicit subquestions with a shared byte budget; no model calls or admission."""
from .passages import SEARCH_LIMIT, lexical_ranges
from .source import SourceError, integer


def merge_ranges(ranges):
    merged = []
    for start, end in sorted(set(tuple(r) for r in ranges)):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])
    return merged


def prepare_subquestions(adapter, revision, specification, budget=12000, top_k=1, strategy="paragraphs-equal"):
    """References are caller-declared byte intervals, never an answer oracle.

    Equal per-question quotas are deliberately conservative: no unused budget
    redistribution, and no claim of exhaustive search or semantic coverage.
    """
    if strategy not in ('paragraphs-equal', 'functions-adaptive'):
        raise SourceError('invalid_retrieval_strategy')
    integer(budget, 1, SEARCH_LIMIT, 'invalid_content_budget')
    integer(top_k, 1, 32, 'invalid_top_k')
    if not isinstance(specification, dict) or set(specification) != {'schema', 'questions'} or specification['schema'] != 'agora/subquestions-input/v1-experimental':
        raise SourceError('invalid_subquestions_specification')
    questions = specification['questions']
    if not isinstance(questions, list) or not 1 <= len(questions) <= 32 or budget < len(questions):
        raise SourceError('invalid_subquestions_count_or_budget')
    ids = set()
    for q in questions:
        if not isinstance(q, dict) or set(q) != {'id', 'query', 'reference_ranges'}:
            raise SourceError('invalid_subquestion')
        if any(type(q[k]) is not str or not q[k].strip() or len(q[k]) > 2000 for k in ('id', 'query')) or q['id'] in ids:
            raise SourceError('invalid_subquestion_identity_or_query')
        ids.add(q['id'])
        refs = q['reference_ranges']
        if not isinstance(refs, list) or len(refs) > 32:
            raise SourceError('invalid_reference_ranges')
        for r in refs:
            if not isinstance(r, list) or len(r) != 2 or any(type(n) is not int for n in r) or not 0 <= r[0] < r[1]:
                raise SourceError('invalid_reference_ranges')
    inventory = adapter.inventory(revision)
    size = inventory['source']['source_bytes']
    if size > SEARCH_LIMIT:
        raise SourceError('search_source_limit_exceeded')
    full = adapter.fetch(revision, [(0, size)], content_budget=SEARCH_LIMIT)
    # Validate reference offsets against this exact source, including UTF-8 edges.
    for q in questions:
        for r in q['reference_ranges']:
            adapter.fetch(revision, [tuple(r)], content_budget=SEARCH_LIMIT)
    if strategy == 'functions-adaptive':
        from .function_retrieval import select
        ranges, reports = select(full, questions, budget, top_k, merge_ranges)
    else:
        quota = budget // len(questions)
        ranges, reports = [], []
        for q in questions:
            selected, retrieval = lexical_ranges(full, q['query'], quota, top_k)
            ranges.extend(selected)
            reports.append(dict(id=q['id'], query=q['query'], quota_bytes=quota,
                                candidate_status='retrieved' if selected else 'no_candidates_within_quota',
                                retrieval=retrieval, selected_ranges=selected))
    combined = merge_ranges(ranges)
    envelope = adapter.fetch(revision, [tuple(r) for r in combined], content_budget=budget) if combined else None
    for q, report in zip(questions, reports):
        missing = [r for r in q['reference_ranges'] if not any(a <= r[0] and b >= r[1] for a, b in combined)]
        report.update(reference_ranges=q['reference_ranges'], missing_reference_ranges=missing,
                      reference_coverage='unknown' if not q['reference_ranges'] else 'partial' if missing else 'covered',
                      semantic_support='not_verified')
    return dict(schema='agora/subquestions-plan/v1-experimental' if strategy == 'paragraphs-equal' else 'agora/subquestions-plan/v2-experimental', source_sha256=revision,
                source_id=adapter.source_id, budget_bytes=budget, top_k=top_k,
                allocation='equal_quotas_without_redistribution' if strategy == 'paragraphs-equal' else 'initial_equal_then_shared_remainder', questions=reports,
                envelope=envelope, delivered_bytes=envelope['delivered_bytes'] if envelope else 0,
                reference_basis='caller_declared_ranges_not_exhaustive',
                global_completeness='not_established', semantic_support='not_verified',
                provider_calls=0, memory_admission='not_performed')
