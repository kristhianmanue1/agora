"""Six authored minimal pairs; generated fixtures are not model responses."""
from pathlib import Path
import hashlib
import json
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter, digest

BASE = Path(__file__).resolve().parent
PAIRS = [
    ('quantity', 'support', 'claim',
     'How many samples passed the Cedar assay?',
     'The Cedar assay tested 30 samples. Exactly 18 samples passed; the remaining 12 failed.',
     'Exactly 18 samples passed the Cedar assay.',
     'Exactly 19 samples passed the Cedar assay.', 'contradicted', 'relevant'),
    ('latest', 'support', 'reference',
     'As of 1 June 2031, which is the latest release of the fictional Lumen toolkit?',
     'Release Vale of the fictional Lumen toolkit was published on 1 May 2031. As of 1 June 2031, Vale is its latest release.',
     'As of 1 June 2031, Vale is the latest release of the fictional Lumen toolkit.',
     'Release Vale of the fictional Lumen toolkit was published on 1 May 2031.', 'insufficient', 'relevant'),
    ('year', 'relevance', 'question',
     'What was the registration fee for the fictional Delta workshop in 2030?',
     'For the fictional Delta workshop in 2030, the registration fee was 40 credits.',
     'The registration fee for the fictional Delta workshop in 2030 was 40 credits.',
     'What was the registration fee for the fictional Delta workshop in 2031?', 'supported', 'extra'),
    ('subject', 'relevance', 'question',
     'What was the measured mass of specimen Aster?',
     'The measured mass of specimen Aster was 12 grams.',
     'The measured mass of specimen Aster was 12 grams.',
     'What was the measured mass of specimen Birch?', 'supported', 'extra'),
    ('author', 'provenance', 'reference',
     'What distance did the rover travel in the trial?',
     'This memo was written by Mira Sol. The rover traveled 42 meters in the trial.',
     'According to Mira Sol\'s memo, the rover traveled 42 meters in the trial.',
     'The rover traveled 42 meters in the trial.', 'insufficient', 'relevant'),
    ('publication', 'provenance', 'reference',
     'How long did the beacon remain active during the test?',
     'Observatory Bulletin No. 8 reports: The beacon remained active for 7 minutes during the test.',
     'According to Observatory Bulletin No. 8, the beacon remained active for 7 minutes during the test.',
     'The beacon remained active for 7 minutes during the test.', 'insufficient', 'relevant'),
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
            rank = hashlib.sha256(('agora-review-controls-01' + identity).encode()).hexdigest()
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
        cases.append({'id': cid, 'candidate': cid + '.json', 'source': cid + '.txt'})
        gold[cid] = {k: item[k] for k in ('pair', 'dimension', 'changed_field', 'positive', 'expected')}
    (out / 'cases.json').write_text(json.dumps(cases, indent=2))
    (out / 'gold.json').write_text(json.dumps(gold, indent=2))
    print('Prepared 12 new English fixtures; expected labels held separately.')

if __name__ == '__main__':
    main()
