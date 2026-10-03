"""Replay frozen selection, not sample discovery; no network calls."""
import hashlib
import json
from pathlib import Path
from agora.qasper import render
from agora.passages import lexical_ranges
from selector import select

here = Path(__file__).resolve().parent
root = here.parents[1]
load = lambda name: json.loads((here/name).read_text())
sha = lambda raw: hashlib.sha256(raw).hexdigest()
freeze = load('freeze.json')
assert sha((here/'selector.py').read_bytes()) == freeze['selector_sha256']
raw_dataset = (root/'experiments/qasper-v1/inputs/test.json').read_bytes()
assert sha(raw_dataset) == freeze['dataset_sha256']
data = json.loads(raw_dataset)
selections = load('selections.json')
result = load('result.json')
assert len(selections) == len(result['rows']) == 16
assert result['http_attempts'] == 0
for row, scored in zip(selections, result['rows']):
    assert all(scored[k] == v for k,v in row.items())
    case = next(c for c in freeze['cases'] if c['id'] == row['document'])
    raw, _ = render(data[case['id']])
    assert sha(raw) == case['sha256']
    if row['method'] == 'comparison-chain':
        selected = select(raw, case['question'], row['budget'])['ranges']
    else:
        envelope = {'spans':[{'text':raw.decode()}], 'source':{'source_bytes':len(raw)}}
        selected, _ = lexical_ranges(envelope, case['question'], row['budget'], 6, ranking='idf')
    assert [list(r) for r in selected] == row['ranges']
    assert sum(b-a for a,b in selected) == row['bytes'] <= row['budget']
    for a,b in selected: raw[a:b].decode()
    for annotation in scored['annotations']:
        assert annotation['covered'] == sum(any(c<=a and b<=d for c,d in selected) for a,b in annotation['ranges'])
print('OK: 16 frozen selections reproduced, source hashes, byte budgets, annotation coverage arithmetic; semantic correctness not certified')
