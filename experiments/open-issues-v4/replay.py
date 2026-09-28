"""Offline, explicitly attributed adaptation of preserved model responses."""
import hashlib
import json
from pathlib import Path
import protocol
BASE=Path(__file__).resolve().parent

def main():
    results=[]
    for case in json.loads((BASE/'replay-fixtures.json').read_text()):
        content=case['original_content']
        if hashlib.sha256(content.encode()).hexdigest()!=case['original_content_sha256']:
            raise ValueError('original_content_changed')
        original=json.loads(content)
        candidate=protocol.prepare_candidate(content,case['input'])
        assert candidate['fields']==original['fields'] and candidate['reason']==original['reason']
        encoded=json.dumps(candidate,ensure_ascii=False,sort_keys=True)
        checked=protocol.validate(encoded,case['input'])
        assert checked['status']=='partial' and checked['fields']['date']['support_status']==case['expected_support']
        results.append(dict(case=case['name'],original_content_sha256=case['original_content_sha256'],candidate_sha256=hashlib.sha256(encoded.encode()).hexdigest(),adapter='host prepare_candidate; schema and scope only',model_fields_unchanged=True,assessment=checked))
    report=dict(status='complete',real_model_calls=0,historical_v3_results_unchanged=True,validator_sha256=hashlib.sha256((BASE/'protocol.py').read_bytes()).hexdigest(),results=results)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
