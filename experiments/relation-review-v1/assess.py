"""Offline relation-review integrity and producer-label comparison."""
from pathlib import Path
import hashlib,json

def assess(directory):
    p=Path(directory)
    load=lambda name:json.loads((p/name).read_text())
    f=load('freeze.json');raw=(p/'request.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=f['request_sha256']:
        raise ValueError('request_digest_mismatch')
    request=json.loads(raw);review=load('review.json')
    if review['status']!='complete':
        raise ValueError('review_not_complete')
    expected=f['producer_expectations'];answers=review['response']['answers']
    if set(expected)!=set(answers) or set(answers)!=set(request['questions']):
        raise ValueError('answer_keys_mismatch')
    disagreements=[];binary_matches=0
    for key,label in expected.items():
        actual=answers[key]['choice']
        if actual not in request['questions'][key]['criteria']:
            raise ValueError('invalid_choice')
        if label!=actual:disagreements.append({'id':key,'producer':label,'reviewer':actual})
        binary_matches+=(label=='supported')==(actual=='supported')
    usage=review['response']['usage']
    return {'cases':len(expected),'exact_matches':len(expected)-len(disagreements),'supported_vs_other_matches':binary_matches,'disagreements':disagreements,'observed_tokens':usage['input_tokens']+usage['output_tokens'],'http_attempts':review['http_attempts'],'label_authority':'producer_only','promotion':'none','semantic_admission':False}

if __name__=='__main__':
    print(json.dumps(assess(Path(__file__).parent),indent=2))
