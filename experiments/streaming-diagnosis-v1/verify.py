"""Offline verification of preserved diagnosis; never calls a provider."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def read(name):
    return json.loads((HERE / name).read_text())

def main():
    freeze = read('freeze.json')
    request_bytes = (HERE / 'request.json').read_bytes()
    assert hashlib.sha256(request_bytes).hexdigest() == freeze['request_sha256']
    state = json.loads(json.loads(request_bytes)['state'])
    source = state['paper'].encode()
    assert hashlib.sha256(source).hexdigest() == freeze['source_sha256']
    plan = read('manual-plan.json')
    diagnosis = read('diagnosis.json')
    assert plan['source_sha256'] == freeze['source_sha256']
    spans = plan['envelope']['spans']
    assert len(spans) == len(diagnosis['chain']) == 3
    for span, evidence in zip(spans, diagnosis['chain']):
        raw = source[span['start_byte']:span['end_byte']]
        assert raw.decode() == span['text'] == evidence['text']
        assert hashlib.sha256(raw).hexdigest() == span['sha256']
        assert [span['start_byte'], span['end_byte']] == [evidence['start_byte'], evidence['end_byte']]
    assert plan['ranges'] == [[s['start_byte'], s['end_byte']] for s in spans]
    assert sum(s['end_byte'] - s['start_byte'] for s in spans) == 715 == diagnosis['manual_bytes'] == plan['envelope']['delivered_bytes']
    assert diagnosis['manual_selection'] and diagnosis['not_held_out_anymore']
    prior = json.loads((ROOT / 'experiments/section-comparison-v1/result.json').read_text())
    rows = [r for r in prior['rows'] if r['document'] == '1907.12984' and r['question_id'] == 'ea6edf45f094586caf4684463287254d44b00e95']
    assert len(rows) == len(diagnosis['prior_selection_coverage']) == 8
    for observed in diagnosis['prior_selection_coverage']:
        row = next(r for r in rows if r['method'] == observed['method'] and r['budget'] == observed['budget'])
        assert row['delivered_bytes'] == observed['delivered_bytes']
        coverage = [any(a <= e['start_byte'] and b >= e['end_byte'] for a, b in row['ranges']) for e in diagnosis['chain']]
        assert coverage == observed['evidence_chain_coverage']
    review = read('review.json')
    assert review['status'] == 'complete' and review['http_attempts'] == 1
    answers = review['response']['answers']
    assert answers['C']['choice'] == 'unsupported'
    assert answers['D']['choice'] == 'supported'
    assert answers['A_evidence']['choice'] != freeze['producer_expectations']['A_evidence']
    usage = review['response']['usage']
    assert usage['input_tokens'] + usage['output_tokens'] == 11811
    print('OK: preserved request/source hashes, 3 exact spans / 715 bytes, controls, disagreement, 11811 observed tokens; no semantic adjudication')

if __name__ == '__main__':
    main()
