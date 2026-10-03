"""Experimental additive retrieval using explicit source labels; no entity claims."""
import hashlib
import re
from agora.weighted_terms import scores


def paragraphs(raw):
    offset = 0
    out = []
    for text in re.split(r'(?:\r?\n){2,}', raw.decode('utf-8')):
        piece = text.encode()
        if piece:
            a = raw.index(piece, offset)
            out.append((a, a + len(piece), text))
            offset = a + len(piece)
    return out


def expand(raw, question, previous, budget):
    if type(budget) is not int or budget < 1:
        raise ValueError('invalid_budget')
    digest = hashlib.sha256(raw).hexdigest()
    if previous['source_sha256'] != digest or previous['question'] != question:
        raise ValueError('source_or_question_changed')
    ps = paragraphs(raw)
    indices = {(a,b): i for i,(a,b,_) in enumerate(ps)}
    selected = set()
    for span in previous['ranges']:
        if not isinstance(span, (list, tuple)) or len(span) != 2 or any(type(x) is not int for x in span):
            raise ValueError('invalid_span')
        key = tuple(span)
        if key not in indices or indices[key] in selected:
            raise ValueError('invalid_or_duplicate_paragraph')
        selected.add(indices[key])
    used = sum(ps[i][1]-ps[i][0] for i in selected)
    if used > budget:
        raise ValueError('budget_below_preserved_content')
    weights = scores([p[2] for p in ps], question)
    # Labels must be explicit paragraph-leading definitions, not model inventions.
    labels = set()
    for _,_,text in ps:
        match = re.match(r'^([A-Za-z][A-Za-z0-9 _-]{1,48}):\s+\S', text)
        if match:
            labels.add(match[1].casefold())
    occurrences = {label: {i for i,p in enumerate(ps) if re.search(r'(?<!\w)'+re.escape(label)+r'(?!\w)',p[2],re.I)} for label in labels}
    additions = []
    while True:
        active = {label for label, ids in occurrences.items() if ids & selected}
        ranked = []
        for i,(a,b,text) in enumerate(ps):
            if i in selected or used+b-a > budget:
                continue
            links = sorted(label for label in active if i in occurrences[label])
            if links:
                ranked.append((-len(links), -weights[i], i, links))
        if not ranked:
            break
        _,_,i,links = min(ranked)
        selected.add(i)
        used += ps[i][1]-ps[i][0]
        additions.append({'range':[ps[i][0],ps[i][1]],'shared_labels':links})
    return {'source_sha256':digest,'question':question,
            'ranges':[[ps[i][0],ps[i][1]] for i in sorted(selected)],
            'delivered_bytes':used,'additions':additions,
            'link_semantics':'literal_label_overlap_only',
            'semantic_completeness':'not_established'}
