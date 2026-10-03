"""Frozen experimental English comparison retrieval; no annotation input."""
import re
from agora.weighted_terms import scores

ROLES = {
    'baseline': r'\b(baselines?|benchmarks?|compared|compare|comparison)\b',
    'input': r'\b(input|inputs|sentence|sentences|document|documents|segment|segments|token|tokens|streaming|offline)\b',
    'evaluation': r'\b(evaluation|evaluate|evaluated|results?|accuracy|latency|bleu|performance)\b',
}

def select(raw, question, budget):
    if type(budget) is not int or budget < 1:
        raise ValueError('invalid_budget')
    text = raw.decode('utf-8')
    spans = []
    cursor = 0
    for block in re.split(r'(?:\r?\n){2,}', text):
        piece = block.encode()
        if piece:
            start = raw.index(piece, cursor)
            spans.append((start, start + len(piece), block))
            cursor = start + len(piece)
    weights = scores([p[2] for p in spans], question)
    queues = []
    for pattern in ROLES.values():
        candidates = [i for i, p in enumerate(spans) if re.search(pattern, p[2], re.I)]
        queues.append(sorted(candidates, key=lambda i: (-weights[i], spans[i][0])))
    chosen = set()
    used = 0
    # Round-robin whole paragraphs; no quota stranded and no partial UTF-8.
    while any(queues):
        for queue in queues:
            if not queue:
                continue
            i = queue.pop(0)
            size = spans[i][1] - spans[i][0]
            if i not in chosen and used + size <= budget:
                chosen.add(i)
                used += size
    return {'ranges': [[spans[i][0], spans[i][1]] for i in sorted(chosen)],
            'delivered_bytes': used, 'semantic_completeness': 'not_established'}
