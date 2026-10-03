"""Offline comparison, freezes cases before reading answer annotations."""
import json, hashlib, re, sys
from pathlib import Path
from datetime import datetime, timezone
from agora.qasper import render
from agora.passages import lexical_ranges
from selector import select

root = Path(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(exist_ok=False)
sha = lambda raw: hashlib.sha256(raw).hexdigest()
dataset = (root/'experiments/qasper-v1/inputs/test.json').read_bytes()
data = json.loads(dataset)
seen = set()
for path in (root/'experiments').rglob('freeze.json'):
    seen.update(re.findall(r'\b\d{4}\.\d{4,5}\b', path.read_text(errors='replace')))
cases = []
for pid, paper in sorted(data.items()):
    raw, _ = render(paper)
    if pid in seen or not 25000 <= len(raw) <= 100000:
        continue
    question = next((q for q in paper['qas'] if re.search(r'\b(compar\w*|baseline\w*|outperform\w*)\b', q['question'], re.I)), None)
    if question:
        cases.append({'id':pid,'question_id':question['question_id'],'question':question['question'],'sha256':sha(raw),'bytes':len(raw)})
    if len(cases)==3: break
assert len(cases)==3
known = data['1907.12984']['qas'][1]
cases.insert(0, {'id':'1907.12984','question_id':known['question_id'],'question':known['question'],'known':True,'sha256':sha(render(data['1907.12984'])[0])})
freeze = {'frozen_at':datetime.now(timezone.utc).isoformat(),'dataset_sha256':sha(dataset),'selector_sha256':sha(Path(__file__).with_name('selector.py').read_bytes()),'cases':cases,'budgets':[5000,12000],'selection_rule':'first 3 sorted absent-from-prior-freeze-files papers 25-100KB with first comparison/baseline/outperform question; no answer filtering','limits':['Novelty is relative to prior freeze.json files only; not guaranteed global holdout.','No API calls; annotation recall is not answer correctness.']}
(out/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
rows=[]
for case in cases:
    raw,_=render(data[case['id']]); assert sha(raw)==case['sha256']
    full={'spans':[{'text':raw.decode()}],'source':{'source_bytes':len(raw)}}
    for budget in freeze['budgets']:
        for method in ('idf','comparison-chain'):
            if method=='idf':ranges,_=lexical_ranges(full,case['question'],budget,6,ranking='idf')
            else:ranges=select(raw,case['question'],budget)['ranges']
            used=sum(b-a for a,b in ranges);assert used<=budget
            rows.append(dict(document=case['id'],question_id=case['question_id'],budget=budget,method=method,ranges=ranges,bytes=used))
(out/'selections.json').write_text(json.dumps(rows,indent=2)+'\n')
# Only now access annotations.
for row in rows:
    paper=data[row['document']];raw,_=render(paper)
    qa=next(q for q in paper['qas'] if q['question_id']==row['question_id'])
    checks=[]
    for answer in qa['answers']:
        a=answer['answer'];mapped=[];unmapped=[]
        for evidence in a['evidence']:
            value=evidence.strip().encode();start=raw.find(value) if value else -1
            if start<0:unmapped.append(evidence)
            else:mapped.append([start,start+len(value)])
        checks.append(dict(unanswerable=a['unanswerable'],ranges=mapped,unmapped=unmapped,covered=sum(any(c<=x and y<=d for c,d in row['ranges']) for x,y in mapped)))
    row['annotations']=checks
(out/'result.json').write_text(json.dumps({'http_attempts':0,'rows':rows},indent=2)+'\n')
for r in rows: print(r['document'],r['budget'],r['method'],r['bytes'],[(a['covered'],len(a['ranges']),len(a['unmapped']),a['unanswerable']) for a in r['annotations']])
