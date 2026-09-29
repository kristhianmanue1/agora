"""Opt-in numbered-item retrieval; exact spans, heuristic structure, no inference."""
import re
from .passages import terms
from .source import SourceError


def candidates(text):
    result = []
    # A blank line containing spaces is still a paragraph separator.
    blocks = list(re.finditer(r'[^\n]*(?:\n(?![ \t]*\n)[^\n]*)*', text))
    header = None
    byte_cursor = 0
    char_cursor = 0
    for block in blocks:
        value = block.group()
        start = byte_cursor + len(text[char_cursor:block.start()].encode('utf-8'))
        end = start + len(value.encode('utf-8'))
        byte_cursor, char_cursor = end, block.end()
        if not value.strip():
            continue
        if '[PDF page ' in value:
            header = None  # Never inherit ownership across pages without evidence.
            continue
        if re.match(r'^\s*\d+(?:\.\d+)+\s+\D', value):
            header = (start, end, value)
            continue
        if not re.match(r'^\s*\d+\.[ \t]+\D', value):
            continue
        ranges = [(start, end)]
        if header:
            ranges.insert(0, (header[0], header[1]))
        result.append(dict(ranges=ranges, text=value,
                           heading=header[2] if header else ''))
        if len(result) > 65536:
            raise SourceError('function_limit_exceeded')
    return result


def select(full, questions, budget, top_k, merge):
    units = candidates(full['spans'][0]['text'])
    ranked = []
    for q in questions:
        words = terms(q['query'])
        matches = [(i, len(words & terms(u['text'])), len(words & terms(u['heading']))) for i,u in enumerate(units)]
        # Heading and item both contribute; neither is semantic verification.
        ranked.append([i for i,body,head in sorted(matches,key=lambda x:(-x[1]-x[2],-x[2],x[0])) if body])
    chosen = [[] for q in questions]
    combined = []
    quota = budget // len(questions)
    def cost(ranges):
        return sum(b-a for a,b in merge(ranges))
    def choose(qi, limit):
        nonlocal combined
        for index in ranked[qi]:
            if index in chosen[qi]:
                continue
            proposal = units[index]['ranges']
            if cost(combined+proposal) <= budget and cost([r for i in chosen[qi]+[index] for r in units[i]['ranges']]) <= limit:
                chosen[qi].append(index)
                combined = merge(combined+proposal)
                return True
        return False
    # Fair first pass, then spend unused quota without exceeding the common cap.
    for qi in range(len(questions)):
        choose(qi, quota)
    for step in range(top_k):
        for qi in range(len(questions)):
            if len(chosen[qi]) < top_k:
                choose(qi, budget)
    reports = []
    for qi,q in enumerate(questions):
        selected = merge([r for i in chosen[qi] for r in units[i]['ranges']])
        reports.append(dict(id=q['id'],query=q['query'],quota_bytes=quota,
            candidate_status='retrieved' if selected else 'no_candidates_within_budget',
            retrieval=dict(method='numbered-items-with-local-heading/v1-experimental',
                candidate_count=len(ranked[qi]),selected_items=chosen[qi],
                search_exhaustive_for_meaning=False),selected_ranges=selected))
    return combined,reports
