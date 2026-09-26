"""Verify frozen inputs and quote navigation independently of model judgments."""
import hashlib,json,sys
from pathlib import Path


def audit(directory):
    root=Path(directory)
    load=lambda name:json.loads((root/name).read_text())
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    if not (root/'summary.json').exists():raise ValueError('run_not_closed')
    if any(digest(root/name)!=value for name,value in load('freeze.json').items()):
        raise ValueError('frozen_input_changed')
    packet=load('packet.json');original=load('meeting-v2.json')
    if packet['revision']!=original['revision'] or packet['source_id']!=original['source_id']:
        raise ValueError('wrong_revision')
    if digest(root/'meeting-v2.json')!=packet['source_sha256'] or digest(root/'source.txt')!=packet['content_sha256']:
        raise ValueError('source_hash_mismatch')
    original_segments={s['id']:s for s in original['segments']}
    for span in packet['spans']:
        segment=original_segments[span['locator']['id']]
        if span['text']!=segment['text'] or any(segment[k]!=v for k,v in span['locator'].items()):
            raise ValueError('invalid_source_mapping')
        if (root/'source.txt').read_bytes()[span['start_byte']:span['end_byte']].decode()!=span['text']:
            raise ValueError('invalid_derived_range')
    candidate=load('candidate.json')
    if candidate['execution_status']!='complete':return {'integrity':'verified','candidate_complete':False,'quotes':0}
    citations=candidate['citations'];navigation=load('navigation.json')
    if len(citations)!=len(navigation):raise ValueError('incomplete_navigation')
    for citation,entry in zip(citations,navigation):
        if any(entry[k]!=citation[k] for k in ('part_id','claim_index','quote')):raise ValueError('citation_mismatch')
        claim=next(p for p in candidate['parts'] if p['id']==entry['part_id'])['claims'][entry['claim_index']]
        if citation['quote']!=claim['quotes'][citation['quote_index']]:raise ValueError('claim_quote_mismatch')
        if not entry['locators']:raise ValueError('missing_locator')
        for locator in entry['locators']:
            segment=original_segments[locator['id']]
            if entry['quote'] not in segment['text'] or any(segment[k]!=v for k,v in locator.items()):
                raise ValueError('quote_not_in_original')
    return {'integrity':'verified','candidate_complete':True,'quotes':len(navigation),'source_revision':original['revision'],
            'semantic_correctness':'requires_separate_assessment'}

if __name__=='__main__':print(json.dumps(audit(sys.argv[1])))
