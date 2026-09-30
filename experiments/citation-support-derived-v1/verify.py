import json,hashlib,copy,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.evidence_ids import validate_ids
from agora.evidence import EvidencePolicy
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=load(B/'fidelity-freeze.json');old=B.parent/'citation-grouping-heldout-v1';assert sha(old/'runs-glm/case-2/response.json')==f['original_response_sha256'];assert sha(old/'runs-glm/case-2/candidate.json')==f['original_candidate_sha256'];assert sha(B/'inputs/candidate.json')==f['derived_candidate_sha256']
a=json.loads(load(old/'runs-glm/case-2/response.json')['content']);b=copy.deepcopy(a);b['parts'][0]['claims'][2]['evidence_ids']+=f['added_ids'];response=load(B/'inputs/response.json');assert json.loads(response['content'])==b;c=load(B/'inputs/candidate.json');parts,errors,_=validate_ids(response,c['evidence_units'],['P1'],EvidencePolicy());assert not errors and parts==c['parts']
for case in load(B/'inputs/fidelity/cases.json'):
 j=load(B/'runs-fidelity'/f"{case['id']}.json");assert json.loads(j['request']['state'])==case['state'];assert set(j['response']['answers'])=={'C3'}
print('OK: only three IDs added, original text and artifacts unchanged, derivative validates, reviewer inputs verified; zero HTTP')
