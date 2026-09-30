import json,hashlib,sys,random
from pathlib import Path
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'src'))
from agora.routed_query import validate_profile_answer
b=r/'experiments/retrieval-answer-paired-v1';pending=set(json.loads((b/'continuation-01.json').read_text())['pending_ids']);key=[c for c in json.loads((b/'key.json').read_text()) if c['id'] in pending];cases=[];validation=[]
for c in key:
 path=b/'runs-generation-02'/(c['id']+'.json');x=json.loads(path.read_text()) if path.exists() else {'status':'not_run'};row=dict(id=c['id'],transport_status=x['status'],valid=False)
 try:
  if x['status']!='completed':raise ValueError('not_run_after_three_errors' if x['status']=='not_run' else 'transport_failure')
  raw=x['response']['choices'][0];env=json.loads((b/'inputs'/f"{c['id']}-envelope.json").read_text());resp=dict(finish_reason=raw.get('finish_reason'),content=raw['message']['content']);parts,_=validate_profile_answer(resp,'\n'.join(s['text'] for s in env['spans']),['P1'],'concise-v1')
  for p in parts:
   for quote in p['quotes']:
    if not any(quote in span['text'] for span in env['spans']):raise ValueError('quote_outside_literal_passage')
  row.update(valid=True,answer_status=parts[0]['status'],answer_sha256=hashlib.sha256(json.dumps(parts,sort_keys=True).encode()).hexdigest())
  full=(b/'inputs'/f"{c['document_id']}.txt").read_text();cases.append(dict(id=c['id'],task=c['question'],evidence=full,answer=parts[0]))
 except Exception as exc:row['diagnostic']=str(exc)[:200]
 validation.append(row)
random.Random('paired-review-v1').shuffle(cases);out=b/'inputs/review-02';out.mkdir();(out/'cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n');(b/'validation-02.json').write_text(json.dumps(validation,indent=2)+'\n');(b/'review-freeze-02.json').write_text(json.dumps(dict(cases_sha256=hashlib.sha256((out/'cases.json').read_bytes()).hexdigest(),max_calls=len(cases),reviewer='jev-1.13.0',retries=0,timeout_seconds=90,blinding='no method, retrieval ranges, gold or sibling response sent; neutral ids; shuffled order'),indent=2)+'\n');print('Valid for review:',len(cases),'of',len(key));print([x for x in validation if not x['valid']])
