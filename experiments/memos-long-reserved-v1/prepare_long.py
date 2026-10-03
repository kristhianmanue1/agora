import json,re,hashlib
from pathlib import Path
root=Path('/Users/krisnova/www/aria/agora');out=Path('/tmp/memos-long-reserved-v1');out.mkdir(exist_ok=False)
dataset=root/'experiments/qasper-v1/inputs/test.json';d=json.loads(dataset.read_text());seen=set()
for p in (root/'experiments').rglob('*'):
 if p.is_file() and p.suffix in ('.json','.md','.txt','.py') and 'inputs' not in p.parts and p.stat().st_size<2000000:
  seen.update(re.findall(r'\b\d{4}\.\d{4,5}\b',p.read_text(errors='replace')))
selected=[];gold=[]
for ident in sorted(d):
 if ident in seen:continue
 doc=d[ident];text=doc['title']+'\n\n'+doc['abstract']+'\n\n'+'\n\n'.join(s['section_name']+'\n'+'\n\n'.join(s['paragraphs']) for s in doc['full_text'])
 if not 40000<=len(text.encode())<=100000 or len(doc['qas'])<2:continue
 filename=ident+'.txt';(out/filename).write_text(text)
 qs=[]
 for i,q in enumerate(doc['qas'][:2]):
  qid=ident+'-q'+str(i+1);qs.append({'id':qid,'question':q['question'],'question_id':q['question_id']});gold.append({'id':qid,'answers':q['answers']})
 selected.append({'id':ident,'source':filename,'bytes':len(text.encode()),'sha256':hashlib.sha256(text.encode()).hexdigest(),'questions':qs})
 if len(selected)==2:break
assert len(selected)==2
(out/'cases.json').write_text(json.dumps(selected,indent=2));(out/'gold.json').write_text(json.dumps(gold,indent=2))
(out/'freeze.json').write_text(json.dumps({'dataset_sha256':hashlib.sha256(dataset.read_bytes()).hexdigest(),'selection':'first sorted unseen IDs, 40-100k UTF8 bytes, first two questions; labels not used for selection','excluded_ids':sorted(seen),'cases_sha256':hashlib.sha256((out/'cases.json').read_bytes()).hexdigest(),'gold_sha256':hashlib.sha256((out/'gold.json').read_bytes()).hexdigest(),'memos_max_requests':14,'agora_max_calls':4,'retries':0,'memos_timeout':180,'agora_timeout':180,'content_budget':12000,'top_k':6},indent=2))
print(json.dumps(selected,indent=2))
