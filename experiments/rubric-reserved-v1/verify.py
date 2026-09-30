import json,hashlib,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
subprocess.run([sys.executable,str(B/'reconstruct.py')],check=True)
f=load(B/'freeze.json');r=load(B/'result.json');rubric=load(B/'rubric.json');source=(B/'inputs/source.txt').read_bytes()
assert r['rubric_sha256']==sha(B/'rubric.json')==f['rubric_sha256']
assert r['reviewer']['label']=='deficient' and r['stop_rule_triggered'] and not r['candidate_created']
assert r['glm_generation_calls']==r['glm_rubric_review_calls']==0
for item in rubric['requirements']:
 e=item['evidence'];assert source[e['start_byte']:e['end_byte']].decode()==e['text']
s=load(B/'selection.json');assert f['document_id'] not in s['excluded'];assert s['full_audit_sha256']==f['selection_sha256']
local=B/'runs-rubric-review/rubric-blind-review.json'
if local.exists():
 assert sha(local)==r['reviewer']['journal_sha256'];j=load(local);assert j['response']==r['reviewer']['response'];assert 'answer' not in json.loads(j['request']['state']);assert j['request_sha256']==r['reviewer']['request_sha256']
print('OK: bindings, UTF-8 locators, pre-candidate review and declared stop verified; no semantic adjudication')
