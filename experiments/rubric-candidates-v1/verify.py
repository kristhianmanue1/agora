"""Reproduce generation rejection offline; never dispatch a request."""
import json,hashlib,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.evidence import EvidencePolicy
from agora.evidence_ids import validate_ids
from agora.coverage_cli import prepare
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=load(B/'freeze.json');source=B/'inputs/source.txt';assert sha(source)==f['source_sha256'];assert sha(B/'rubric.json')==f['rubric_sha256'];assert sha(B/'inputs/control.json')==f['control_sha256']
c=load(B/'runs-generation/candidate.json');response=load(B/'runs-generation/response.json');assert c['response']==response;assert response['finish_reason']=='stop'
parts,errors,_=validate_ids(response,c['evidence_units'],['P1'],EvidencePolicy());assert parts is None and errors==c['diagnostics']==[dict(code='part_quote_bytes_exceeded',part_id='P1',observed=15062,limit=12000)]
ids=[i for p in json.loads(response['content'])['parts'] for claim in p['claims'] for i in claim['evidence_ids']];units={u['id']:u for u in c['evidence_units']};total=sum(units[i]['quote_bytes'] for i in ids);unique=sum(units[i]['quote_bytes'] for i in set(ids));assert total==15062 and unique==5097
for u in units.values():assert source.read_bytes()[u['start_byte']:u['end_byte']].decode()==u['text']
prepare(source.read_bytes(),f['source_sha256'],(B/'inputs/control.json').read_bytes(),f['control_sha256'],'P1',f['question'])
assert not (B/'review-freeze.json').exists() and not (B/'inputs/workspace').exists()
print(json.dumps(dict(status='rejection_reproduced',quote_uses=len(ids),unique_units=len(set(ids)),quote_bytes=total,unique_quote_bytes=unique,control_structurally_valid=True,http_calls=0)))
