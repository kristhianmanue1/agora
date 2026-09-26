"""Frozen multiaxis and minimal-pair scoring, retaining failed/missing outcomes."""
from collections import Counter

AXES = ('support', 'relevance', 'language', 'recommendation')
VALUES = {
    'support': {'supported', 'contradicted', 'insufficient'},
    'relevance': {'relevant', 'extra', 'uncertain'},
    'language': {'match', 'mismatch', 'uncertain'},
    'recommendation': {'needs_revision', 'needs_adjudication'},
}

def scores(gold, predictions):
    if set(predictions) - set(gold):
        raise ValueError('unknown_case')
    pairs = {}
    for cid, row in gold.items():
        if type(row['positive']) is not bool:
            raise ValueError('invalid_polarity')
        members = pairs.setdefault(row['pair'], {})
        if row['positive'] in members:
            raise ValueError('duplicate_pair_polarity')
        members[row['positive']] = cid
        if set(row['expected']) != set(AXES) or any(row['expected'][k] not in VALUES[k] for k in AXES):
            raise ValueError('invalid_expectation')
    if any(set(p) != {True, False} for p in pairs.values()):
        raise ValueError('incomplete_pair')
    correct, axis_correct = {}, Counter()
    statuses = Counter()
    for cid, expected in gold.items():
        got = predictions.get(cid)
        if got is None or got in ('failed', 'not_run'):
            statuses['not_run' if got is None else got] += 1
            correct[cid] = False
            continue
        if not isinstance(got, dict) or set(got) != set(AXES) or any(got[k] not in VALUES[k] for k in AXES):
            raise ValueError('invalid_prediction')
        statuses['valid'] += 1
        matches = {k: got[k] == expected['expected'][k] for k in AXES}
        axis_correct.update(k for k, ok in matches.items() if ok)
        correct[cid] = all(matches.values())
    pair_rows = []
    for pair, members in sorted(pairs.items()):
        positive, negative = members[True], members[False]
        pair_rows.append({'pair': pair, 'dimension': gold[positive]['dimension'],
                          'positive_correct': correct[positive], 'negative_correct': correct[negative],
                          'pair_correct': correct[positive] and correct[negative]})
    return {'cases': len(gold), 'statuses': dict(statuses),
            'correct_all_axes': sum(correct.values()),
            'axis_correct': {k: axis_correct[k] for k in AXES},
            'positive_correct': sum(x['positive_correct'] for x in pair_rows),
            'negative_correct': sum(x['negative_correct'] for x in pair_rows),
            'pairs_correct': sum(x['pair_correct'] for x in pair_rows),
            'pairs': pair_rows,
            'scope': 'authored controls; not public benchmark accuracy or approval rate'}
