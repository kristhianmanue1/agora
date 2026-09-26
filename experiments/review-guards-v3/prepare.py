"""Four authored diagnostic pairs; generated fixtures are not model responses."""
from pathlib import Path
import hashlib
import json
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter, digest

BASE = Path(__file__).resolve().parent
PAIRS = [
    ('attributed_account', 'certainty', 'claim',
     'What does the passage report about who built the first Oriole clock?',
     'Nera claimed that she built the first Oriole clock in 1912. This is her unverified account; no independent evidence establishes who built the first one.',
     'Nera claimed that she built the first Oriole clock in 1912.',
     'Nera built the first Oriole clock in 1912.', 'insufficient', 'relevant'),
    ('measurement_binding', 'scope', 'reference',
     'What does the survey say about the 64 km boundary of Zone L?',
     'The 64 km boundary of Zone L includes its inlets. The survey also records an unrelated 19 km boundary of Zone M.',
     'The 64 km boundary of Zone L includes its inlets.',
     'The boundary of Zone L is 64 km; whether it includes inlets is not specified. An unrelated 19 km boundary of Zone M includes its inlets.', 'insufficient', 'relevant'),
    ('answer_relevance', 'relevance', 'question',
     'Which animal did Elian keep in the tower?',
     'Elian lived in a tower. The passage does not identify any animal kept there.',
     'Elian kept a fox in the tower.',
     'Which instrument did Elian play in the tower?', 'insufficient', 'extra'),
    ('exception', 'certainty', 'reference',
     'What is the maximum test duration allowed by protocol K?',
     'Under protocol K, every test must stop after at most 9 minutes. There are no exceptions.',
     'Under protocol K, every test must stop after at most 9 minutes.',
     'Under protocol K, tests normally stop after 9 minutes, but calibration tests may continue for 14 minutes.', 'contradicted', 'relevant'),
]

def main():
    out = BASE / 'inputs/pilot-01'
    out.mkdir(parents=True, exist_ok=False)
    items = []
    for name, dimension, changed, question, reference, claim, alternate, support, relevance in PAIRS:
        for positive in (True, False):
            fields = {'question': question, 'reference': reference, 'claim': claim}
            if not positive:
                fields[changed] = alternate
            identity = hashlib.sha256(json.dumps(fields, sort_keys=True).encode()).hexdigest()
            rank = hashlib.sha256(('agora-review-guards-01' + identity).encode()).hexdigest()
            expected = {'support': 'supported' if positive else support,
                        'relevance': 'relevant' if positive else relevance,
                        'language': 'match',
                        'recommendation': 'needs_adjudication' if positive else 'needs_revision'}
            items.append(dict(fields, identity=identity, rank=rank, pair=name,
                              dimension=dimension, changed_field=changed,
                              positive=positive, expected=expected))
    cases, gold = [], {}
    for i, item in enumerate(sorted(items, key=lambda x: x['rank']), 1):
        cid = f'case-{i:02}'
        source = out / (cid + '.txt')
        source.write_text(item['reference'])
        response = {'parts': [{'id': 'answer', 'status': 'answered', 'claims': [
            {'text': item['claim'], 'quotes': [item['reference']]}], 'missing': []}]}
        candidate = query_evidence(FileSourceAdapter(source, item['identity']), digest(source.read_bytes()),
            item['question'], [{'id': 'answer', 'question': item['question']}],
            lambda s, u: {'finish_reason': 'stop', 'content': json.dumps(response)},
            response_language='en', content_budget=12000)
        assert candidate['execution_status'] == 'complete'
        candidate['artifact_origin'] = 'authored diagnostic fixture; not a model generation'
        (out / (cid + '.json')).write_text(json.dumps(candidate, indent=2))
        if item['pair'] == 'answer_relevance' and item['positive']:
            item['expected']['support'] = 'insufficient'
            item['expected']['recommendation'] = 'needs_revision'
        cases.append({'id': cid, 'candidate': cid + '.json', 'source': cid + '.txt'})
        gold[cid] = {k: item[k] for k in ('pair', 'dimension', 'changed_field', 'positive', 'expected')}
    (out / 'cases.json').write_text(json.dumps(cases, indent=2))
    (out / 'gold.json').write_text(json.dumps(gold, indent=2))
    print('Prepared 8 new English fixtures; expected labels held separately.')

if __name__ == '__main__':
    main()
