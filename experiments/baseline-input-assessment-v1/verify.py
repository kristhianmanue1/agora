"""Verify cited ranges and that the historical v2 candidate stays unchanged."""
from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parent;root=p.parents[1]
a=json.loads((p/'assessment.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
source=json.loads(json.loads((root/'experiments/streaming-diagnosis-v1/request.json').read_text())['state'])['paper'].encode()
assert sha(source)==a['source_sha256']
assert len(a['spans'])==6
for span in a['spans']:
 raw=source[span['start_byte']:span['end_byte']]
 assert raw.decode()==span['text'] and sha(raw)==span['sha256']
candidate=(root/a['candidate_path']).read_bytes();assert sha(candidate)==a['candidate_sha256']
assert json.loads(candidate)['fields']['input']=={'text':None,'evidence_ids':[]}
assert a['provider_calls']==0
print('OK: six exact source spans, original candidate preserved with unknown input; inference not adjudicated')
