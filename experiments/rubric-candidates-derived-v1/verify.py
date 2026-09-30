import json,hashlib,copy,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora import rubric_cli
from agora.evidence_ids import validate_ids
from agora.evidence import EvidencePolicy
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=load(B/'freeze.json');d=load(B/'derivation.json');old=B.parent/'rubric-candidates-v1';original=old/'runs-generation/response.json';assert sha(original)==d['original_response_sha256'];assert sha(old/'runs-generation/candidate.json')==d['original_candidate_sha256'];assert sha(B/'inputs/derived.json')==d['derived_candidate_sha256'];assert sha(B/'inputs/derived-response.json')==d['derived_response_sha256']
before=json.loads(load(original)['content']);expected=copy.deepcopy(before)
for edit in d['removed']:expected['parts'][0]['claims'][edit['claim_index']]['evidence_ids'].remove(edit['evidence_id'])
response=load(B/'inputs/derived-response.json');assert json.loads(response['content'])==expected
candidate=load(B/'inputs/derived.json');parts,errors,_=validate_ids(response,candidate['evidence_units'],['P1'],EvidencePolicy());assert not errors and parts==candidate['parts']
assert sha(old/'rubric.json')==f['rubric_sha256'];rows=[]
for case in f['cases']:
 assert sha(B/case['candidate'])==case['sha256'];result=load(B/('runs-'+case['id'])/'result.json');assert result['candidate_sha256']==case['sha256'];assert result['rubric_sha256']==f['rubric_sha256'];assert result['disposition']=='requires_review' and result['rubric_completeness']=='not_established'
 if result['status']=='complete':
  actual={x['id']:x['status'] for x in rubric_cli.assess(result['response'],['R1','R2','R3','R4'])};assert actual=={x['id']:x['status'] for x in result['requirements']}
 else:actual=None
 rows.append(dict(id=case['id'],status=result['status'],actual=actual,expected=case['expected'],match=actual==case['expected']))
print(json.dumps(rows,indent=2))
