"""Reproduce structural outcome and source partition offline; no HTTP."""
import json,hashlib,re,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.evidence import query_evidence
from agora.evidence_ids import build_units
from agora.source import FileSourceAdapter
from agora.rubric_cli import assess
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=load(B/'freeze.json');source=B.parent/'rubric-candidates-v1/inputs/source.txt';assert sha(source)==f['source_sha256'];assert sha(B.parent/'rubric-candidates-v1/rubric.json')==f['rubric_sha256']
c=load(B/'runs-generation/candidate.json');response=load(B/'runs-generation/response.json');assert c['response']==response
units=build_units(dict(spans=[dict(text=source.read_text(),start_byte=0)]),'qasper:1911.10401',f['source_sha256'],1000);assert units==c['evidence_units'];assert all(u['quote_bytes']<=1000 for u in units)
assert re.sub(r'\s','',source.read_text())==re.sub(r'\s','',''.join(u['text'] for u in units))
for u in units:assert source.read_bytes()[u['start_byte']:u['end_byte']].decode()==u['text']
replayed=query_evidence(FileSourceAdapter(source,'qasper:1911.10401'),f['source_sha256'],f['question'],[dict(id='P1',question=f['question'])],lambda *_:response,content_budget=60000,prompt_budget=100000,citation_mode='ids',response_language='en',max_unit_bytes=1000);assert replayed==c
if (B/'runs-review/result.json').exists():
 r=load(B/'runs-review/result.json');rf=load(B/'review-freeze.json');assert sha(B/'runs-generation/candidate.json')==rf['candidate_sha256']==r['candidate_sha256'];assert r['rubric_sha256']==f['rubric_sha256'];assert r['rubric_completeness']=='not_established'
 if r['status']=='complete':assert assess(r['response'],list(f['expected']))==r['requirements']
print('OK: source/rubric hashes, exact unchanged candidate replay, 59 unit offsets and full non-whitespace source coverage; no HTTP')
