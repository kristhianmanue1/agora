"""Experimental multi-passage consumer; lexical retrieval, no automatic admission."""
import json
import re
from urllib.error import HTTPError
from .source import MAX_ENVELOPE_BYTES, FileSourceAdapter, SourceError, integer, digest
from .query import SYSTEM, validate_answer
from .transform import TransformError

SEARCH_LIMIT = 4 * 1024 * 1024
STOP = set('que qué cual cuál como cómo quien quién para por los las del una unos unas con sin sobre está este esta entre puede'.split())


def terms(text):
    return {word for word in re.findall(r'\w+', text.casefold()) if len(word) > 2 and word not in STOP}


def lexical_ranges(envelope, question, budget, top_k=3):
    """Paragraph matches with adjacent paragraph expansion if the budget allows.

    Empty retrieval is a search outcome, never proof of absence in the source.
    """
    integer(budget, 1, SEARCH_LIMIT, 'invalid_content_budget')
    integer(top_k, 1, 32, 'invalid_top_k')
    text = envelope['spans'][0]['text']
    paragraphs = []
    full = text.encode("utf-8")
    query_terms = terms(question)
    offset = 0
    for block in re.split(r'(?:\r?\n){2,}', text):
        # Locate exact bytes; delimiter gaps are kept outside passage ranges.
        raw = block.encode('utf-8')
        if raw:
            if len(paragraphs) >= 65536:
                raise SourceError("paragraph_limit_exceeded")
            start = full.find(raw, offset)
            paragraphs.append((start, start + len(raw), len(terms(block) & query_terms)))
            offset = start + len(raw)
    ranked = sorted((i for i, p in enumerate(paragraphs) if p[2]),
                    key=lambda i: (-paragraphs[i][2], paragraphs[i][0]))
    selected = set()
    used = 0
    skipped = []
    for i in ranked:
        if len(selected) >= top_k:
            break
        size = paragraphs[i][1] - paragraphs[i][0]
        if used + size <= budget:
            selected.add(i)
            used += size
        else:
            skipped.append(i)
    seeds = sorted(selected)
    for i in seeds:
        for neighbor in (i - 1, i + 1):
            if 0 <= neighbor < len(paragraphs) and neighbor not in selected:
                size = paragraphs[neighbor][1] - paragraphs[neighbor][0]
                if used + size <= budget and len(selected) < 256:
                    selected.add(neighbor)
                    used += size
    ranges = [(paragraphs[i][0], paragraphs[i][1]) for i in sorted(selected)]
    return ranges, {'method': 'lexical-paragraph-overlap/v0.1', 'top_k': top_k,
                    'matching_paragraphs': len(ranked), 'seed_paragraphs': seeds,
                    'selected_paragraphs': sorted(selected), 'oversized_candidates': skipped,
                    'local_scan_bytes': envelope['source']['source_bytes'],
                    'selection_complete': len(selected) == len(paragraphs),
                    'search_exhaustive_for_meaning': False}


def prepare(adapter, revision, question, mode, *, ranges=None,
            content_budget=2048, prompt_budget=65536, top_k=3):
    if type(question) is not str or not question.strip() or len(question) > 2000:
        raise SourceError('invalid_question')
    question.encode('utf-8')
    integer(prompt_budget, 1, MAX_ENVELOPE_BYTES, 'invalid_prompt_budget')
    integer(content_budget, 1, SEARCH_LIMIT, 'invalid_content_budget')
    if mode not in ('source', 'reference', 'retrieve'):
        raise SourceError('invalid_mode')
    if (mode == 'reference') != (ranges is not None):
        raise SourceError('reference_requires_ranges_only')
    inventory = adapter.inventory(revision)
    size = inventory['source']['source_bytes']
    retrieval = {'method': 'explicit_ranges' if mode == 'reference' else 'full_source'}
    if mode == 'source':
        ranges = [(0, size)]
    if mode == 'retrieve':
        if size > SEARCH_LIMIT:
            raise SourceError('search_source_limit_exceeded')
        full = adapter.fetch(revision, [(0, size)], content_budget=SEARCH_LIMIT)
        ranges, retrieval = lexical_ranges(full, question, content_budget, top_k)
        if not ranges:
            return None, retrieval, None
    envelope = adapter.fetch(revision, ranges, content_budget=content_budget)
    user = json.dumps({'question': question, 'parts': [{'id': 'P1', 'question': question}],
                       'document': [{'passage': i + 1, 'text': span['text']}
                                    for i, span in enumerate(envelope['spans'])]}, ensure_ascii=False)
    if len(SYSTEM.encode()) + len(user.encode()) > prompt_budget:
        raise SourceError('prompt_budget_exceeded')
    return envelope, retrieval, user


def query_passages(adapter, revision, question, provider, mode='retrieve', **options):
    """One provider call at most; new schema, deliberately separate from v0.3."""
    result = {'schema': 'agora/passage-query/v0.1', 'question': question, 'mode': mode,
              'source_id': adapter.source_id, 'source_sha256': revision,
              'options': options, 'provider_calls': 0, 'review_status': 'unreviewed',
              'semantic_support': 'not_verified', 'memory_admission': 'not_performed'}
    try:
        envelope, retrieval, user = prepare(adapter, revision, question, mode, **options)
        result['retrieval'] = retrieval
        if envelope is None:
            result.update(execution_status='complete', answer_status='retrieval_budget_exhausted' if retrieval['matching_paragraphs'] else 'no_retrieval_candidates',
                          evidence_sufficiency='unknown', answer='', citations=[])
            return result
        result['envelope'] = envelope
        result['prompt'] = {'system': SYSTEM, 'user': user}
        result['prompt_bytes'] = len(SYSTEM.encode()) + len(user.encode())
        result['provider_calls'] = 1
        response = provider(SYSTEM, user)
        result['response'] = response
        joined = '\n'.join(span['text'] for span in envelope['spans'])
        parts, operation = validate_answer(response, joined, ['P1'])
        part = parts[0]
        citations = []
        for quote in part['quotes']:
            matches = []
            for i, span in enumerate(envelope['spans']):
                pos = span['text'].find(quote)
                if pos >= 0:
                    start = span['start_byte'] + len(span['text'][:pos].encode())
                    matches.append({'passage': i + 1, 'start_byte': start,
                                    'end_byte': start + len(quote.encode())})
            if not matches:
                raise TransformError('quote_outside_literal_passage')
            citations.append({'quote': quote, 'matches': matches,
                              'match_policy': 'first_occurrence_per_passage'})
        result.update(execution_status='complete', answer_status='candidate' if part['status'] == 'answer'
                      else 'not_found_in_supplied_material', answer=part['answer'], citations=citations,
                      normalization=operation, evidence_sufficiency='unknown')
    except (SourceError, TransformError, UnicodeError) as exc:
        result.update(execution_status='rejected', diagnostic=str(exc))
    except Exception as exc:
        result.update(execution_status='failed', diagnostic=type(exc).__name__)
        if isinstance(exc, HTTPError):
            result['transport_error'] = {'kind': 'http_error', 'status': exc.code}
    return result
