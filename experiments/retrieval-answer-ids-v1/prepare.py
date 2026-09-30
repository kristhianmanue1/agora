import json,hashlib,sys,subprocess
from pathlib import Path
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'src'))
from agora.evidence import EvidencePolicy
from agora.evidence_ids import build_units,id_system
old=r/'experiments/retrieval-answer-paired-v1';b=r/'experiments/retrieval-answer-ids-v1';b.mkdir();(b/'inputs').mkdir();(b/'.gitignore').write_text('inputs/\nruns-*/\n')
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
key=json.loads((old/'key.json').read_text());freeze=json.loads((old/'freeze.json').read_text());cases=[];mapping=[];hashes={}
system=id_system(EvidencePolicy()).replace('Answer in Spanish','Answer in English')+'\nWrite every claim text and missing item in English. Include only claims needed to answer the requested aspects.'
for c in key:
 cid='i'+hashlib.sha256((c['id']+':ids-v1').encode()).hexdigest()[:10];envpath=old/'inputs'/f"{c['id']}-envelope.json";env=json.loads(envpath.read_text());hashes[c['id']]=hashlib.sha256(envpath.read_bytes()).hexdigest();source=(old/'inputs'/f"{c['document_id']}.txt").read_bytes();assert hashlib.sha256(source).hexdigest()==freeze['sources'][c['document_id']]
 units=build_units(env,'qasper:'+c['document_id'],freeze['sources'][c['document_id']]);assert all(source[u['start_byte']:u['end_byte']].decode()==u['text'] for u in units)
 user=json.dumps(dict(question=c['question'],aspects=[dict(id='P1',question=c['question'])],evidence_units=[{k:u[k] for k in ('id','text','quote_bytes')} for u in units]),ensure_ascii=False);assert len(system.encode())+len(user.encode())<=65536
 cases.append(dict(id=cid,system=system,user=user));mapping.append(dict(c,id=cid,previous_id=c['id']));dump(b/'inputs'/f'{cid}-units.json',units)
dump(b/'inputs/cases.json',cases);dump(b/'key.json',mapping);dump(b/'freeze.json',dict(code_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),cases_sha256=hashlib.sha256((b/'inputs/cases.json').read_bytes()).hexdigest(),envelope_sha256=hashes,max_generation_calls=24,max_review_calls=24,generator='glm-5.3-flash',reviewer='jev-1.13.0',temperature=0,max_tokens=2048,timeout_seconds=90,retries=0,stop='401/402/403/429 or three transport failures',profile='existing claim-evidence-query/v2 ids, English, default EvidencePolicy',primary='paired supported and complete task answers among both-valid reviewed pairs; report all invalid outputs, partial answers, abstentions, missing pairs and tokens',limitations='Development corpus; one draw; no human adjudication. Previous concise-v1 differs in schema/prompt, so not causal evidence of ID-only benefit. No defaults changed.'))
print('Prepared 24 cases; byte provenance verified')
