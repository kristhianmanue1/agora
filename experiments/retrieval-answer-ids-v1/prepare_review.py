import json,hashlib,sys,random
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'))
from agora.evidence import EvidencePolicy
from agora.evidence_ids import validate_ids
B=Path(__file__).resolve().parent;old=B.parent/'retrieval-answer-paired-v1';cases=[];validation=[]
for c in json.loads((B/'key.json').read_text()):
 p=B/'runs-generation'/f"{c['id']}.json";g=json.loads(p.read_text()) if p.exists() else {'status':'not_run'};row=dict(id=c['id'],transport_status=g['status'],valid=False)
 if g['status']=='completed':
  choice=g['response']['choices'][0];units=json.loads((B/'inputs'/f"{c['id']}-units.json").read_text());parts,errors,anchors=validate_ids(dict(finish_reason=choice.get('finish_reason'),content=choice['message']['content']),units,['P1'],EvidencePolicy());row['diagnostics']=errors
  if not errors:
   row.update(valid=True,answer_status=parts[0]['status'],reference_count=len(anchors))
   # Strip neutral IDs but preserve resolved evidence, claims and missing information.
   answer=dict(status=parts[0]['status'],claims=[dict(text=x['text'],quotes=x['quotes']) for x in parts[0]['claims']],missing=parts[0]['missing'])
   cases.append(dict(id=c['id'],task=c['question'],evidence=(old/'inputs'/f"{c['document_id']}.txt").read_text(),answer=answer))
 validation.append(row)
random.Random('paired-review-v1').shuffle(cases);out=B/'inputs/review-02';out.mkdir();(out/'cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n');(B/'validation.json').write_text(json.dumps(validation,indent=2)+'\n');(B/'review-freeze-02.json').write_text(json.dumps(dict(cases_sha256=hashlib.sha256((out/'cases.json').read_bytes()).hexdigest(),max_calls=len(cases),reviewer='jev-1.13.0',retries=0,timeout_seconds=90,blinding='no method, gold, sibling, retrieval ranges or IDs; full source plus resolved candidate claims and missing items'),indent=2)+'\n');print(json.dumps(dict(valid=len(cases),total=len(validation),rejected=[v for v in validation if not v['valid']])))
