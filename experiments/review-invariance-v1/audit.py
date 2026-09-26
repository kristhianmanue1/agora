"""Offline audit, including partial runs and unavailable responses."""
from pathlib import Path
import hashlib,json
from agora.evidence_review import review_evidence
from score import scores
b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/glm-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((out/'freeze.json').read_text())
assert all(sha(out/n)==h for n,h in frozen.items())
for name in ('worker.py','run.py','prepare.py','score.py','audit.py'):
 assert sha(b/name)==sha(out/name)
for p in (out/'code/agora').glob('*.py'):assert sha(p)==sha(root/'src/agora'/p.name)
cases=json.loads((out/'inputs/cases.json').read_text())
gold=json.loads((out/'inputs/gold.json').read_text())
rows=json.loads((out/'execution.json').read_text())
assert len({r['case'] for r in rows})==len(rows)<=8
assert all(r['case'] in gold and r['version']=='v3' for r in rows)
predictions={};observations=[];pairs={}
for case in cases:
 cid=case['id'];candidate=json.loads((out/'inputs'/case['candidate']).read_text())
 assert sha(b/'inputs'/case['candidate'])==sha(out/'inputs'/case['candidate'])
 question=json.loads(candidate['prompt']['user'])['question']
 claim=candidate['parts'][0]['claims'][0];reference=(out/'inputs'/case['source']).read_text()
 assert claim['quotes']==[reference]
 pairs.setdefault(gold[cid]['pair'],[]).append((claim['text'],claim['quotes'],question))
 ledger=[r for r in rows if r['case']==cid]
 if not ledger:continue
 f=out/'v3'/cid/'result.json'
 if not f.exists():
  assert ledger[0]['sha256'] is None
  predictions[cid]='failed';continue
 assert sha(f)==ledger[0]['sha256']
 r=json.loads(f.read_text())
 request=json.loads(f.with_name('request.json').read_text())
 assert request['response_format']=={'type':'json_object'}
 assert request['model']=='glm-5.3-flash' and request['max_tokens']==8192 and request['temperature']==0
 assert request['messages']==[{'role':'system','content':r['prompt']['system']},{'role':'user','content':r['prompt']['user']}]
 sent=json.loads(r['prompt']['user'])
 assert sent==dict(response_language='en',question=question,aspects=[{'id':'answer','question':question}],claims=[dict(part_id='answer',claim_index=0,text=claim['text'],quotes=[reference])],missing=[dict(part_id='answer',items=[])])
 response=r.get('response')
 if response:
  replay=review_evidence(candidate,lambda s,u:response,response_language='en',review_version='v3')
  for key in ('schema','prompt_revision','candidate_sha256','execution_status','assessment','diagnostics','recommendation'):
   assert replay.get(key)==r.get(key),(cid,key)
  assert response.get('usage',{}).get('total_tokens')==ledger[0]['tokens']
 else:
  assert r['execution_status']=='failed' and ledger[0]['tokens'] is None
 if r['execution_status']=='complete':
  a=r['assessment'];c=a['claims'][0]
  prediction=dict(support=c['support'],relevance=c['relevance'],language=a['language'],recommendation=r['recommendation'])
 else:prediction='failed'
 predictions[cid]=prediction
 observations.append(dict(case=cid,expected=gold[cid]['expected'],observed=prediction,status=r['execution_status'],diagnostics=r.get('diagnostics')))
for pair,items in pairs.items():
 assert len(items)==2 and items[0][:2]==items[1][:2] and items[0][2]!=items[1][2],pair
groups={}
for origin in ('new','regression_not_new'):
 g={k:v for k,v in gold.items() if v['origin']==origin}
 groups[origin]=scores(g,{k:v for k,v in predictions.items() if k in g})
report=dict(freeze_and_local_replay_verified=True,calls=len(rows),metrics=scores(gold,predictions),groups=groups,
 known_tokens=sum(r['tokens'] or 0 for r in rows),unknown_usage=sum(r['tokens'] is None for r in rows),
 seconds=round(sum(r['seconds'] for r in rows),3),observations=observations,
 limits='Diagnostic controls; same-agent audit; no concurrent baseline or generalization.')
(out/'audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
