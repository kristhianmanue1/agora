"""Frozen scoring, deduplication, exact source verification and offline replay."""
from pathlib import Path
from collections import Counter
import csv,hashlib,json
from agora.evidence_review import review_evidence
from score import classification_scores
from prepare import select,MAPPING

b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/glm-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((out/'freeze.json').read_text())
assert all(sha(out/n)==h for n,h in frozen.items())
for n in ('worker.py','run.py','prepare.py','score.py','audit.py'):assert sha(b/n)==sha(out/n)
for p in (out/'code/agora').glob('*.py'):assert sha(p)==sha(root/'src/agora'/p.name)
raw=list(csv.DictReader((out/'inputs/AttrEval-GenSearch.csv').open()))
previous=json.loads((out/'inputs/previous-exposure.json').read_text())
selected,selection=select(raw,previous)
cases=json.loads((out/'inputs/pilot-02/cases.json').read_text());gold=json.loads((out/'inputs/pilot-02/gold.json').read_text())
assert [c['source_row_index'] for c in cases]==[c['row_index'] for c in selected]
rows=json.loads((out/'execution.json').read_text())
assert len(rows)<=48 and len({(x['case'],x['version']) for x in rows})==len(rows)
expected={c['id']:gold[c['id']]['support'] for c in cases};predictions={v:{} for v in ('v1','v2')};details=[]
for case in cases:
 c=json.loads((out/'inputs/pilot-02'/case['candidate']).read_text());original=raw[case['source_row_index']]
 assert sha(b/'inputs/pilot-02'/case['candidate'])==sha(out/'inputs/pilot-02'/case['candidate'])
 assert gold[case['id']]=={'label':original['label'],'support':MAPPING[original['label']]}
 assert c['parts'][0]['claims'][0]['text']==original['answer']
 assert c['parts'][0]['claims'][0]['quotes']==[original['reference']]
 source=(out/'inputs/pilot-02'/case['source']).read_bytes()
 assert source.decode()==original['reference'] and hashlib.sha256(source).hexdigest()==c['source_sha256']
 for version in predictions:
  ledger=[x for x in rows if x['case']==case['id'] and x['version']==version]
  if not ledger:continue
  row=ledger[0];f=out/version/case['id']/'result.json'
  if not f.exists():predictions[version][case['id']]='failed';continue
  r=json.loads(f.read_text());assert sha(f)==row['sha256']
  request=json.loads(f.with_name('request.json').read_text())
  assert request['model']=='glm-5.3-flash' and request['max_tokens']==8192 and request['temperature']==0
  assert request['messages']==[{'role':'system','content':r['prompt']['system']},{'role':'user','content':r['prompt']['user']}]
  sent=json.loads(r['prompt']['user']);q=original['query'] or 'Assess whether the supplied reference supports the answer.'
  assert set(sent)=={'response_language','question','aspects','claims','missing'}
  assert sent['question']==q and sent['response_language']=='en'
  assert sent['aspects']==[{'id':'answer','question':q}] and sent['missing']==[{'part_id':'answer','items':[]}]
  assert sent['claims']==[{'part_id':'answer','claim_index':0,'text':original['answer'],'quotes':[original['reference']]}]
  replay=review_evidence(c,lambda s,u:r['response'],response_language='en',review_version=version)
  for key in ('schema','candidate_sha256','execution_status','assessment','diagnostics','recommendation'):assert replay.get(key)==r.get(key),(case['id'],version,key)
  complete=r['execution_status']=='complete';a=r['assessment'] if complete else None
  prediction=a['claims'][0]['support'] if complete else 'failed';predictions[version][case['id']]=prediction
  details.append({'case':case['id'],'version':version,'gold':expected[case['id']],'prediction':prediction,'correct':prediction==expected[case['id']],
                 'relevance':a['claims'][0]['relevance'] if complete else None,'language':a['language'] if complete else None,
                 'recommendation':r.get('recommendation'),'status':r['execution_status'],'tokens':row['tokens'],'seconds':row['seconds'],'diagnostics':r.get('diagnostics')})
metrics={}
for v in predictions:
 used=[x for x in rows if x['version']==v];d=[x for x in details if x['version']==v]
 metrics[v]=dict(classification_scores(expected,predictions[v]),calls=len(used),tokens=sum(x['tokens'] or 0 for x in used),
                 unknown_usage=sum(x['tokens'] is None for x in used),seconds=round(sum(x['seconds'] for x in used),3),
                 descriptive_relevance_counts=dict(Counter(x['relevance'] or 'unavailable' for x in d)),
                 descriptive_recommendation_counts=dict(Counter(x['recommendation'] or 'unavailable' for x in d)))
paired={'both_correct':0,'v1_only_correct':0,'v2_only_correct':0,'neither_correct':0,'unpaired':0}
for cid,label in expected.items():
 if cid not in predictions['v1'] or cid not in predictions['v2']:paired['unpaired']+=1;continue
 a=predictions['v1'][cid]==label;z=predictions['v2'][cid]==label
 paired['both_correct' if a and z else 'v1_only_correct' if a else 'v2_only_correct' if z else 'neither_correct']+=1
report={'freeze_source_selection_and_replay_verified':True,'calls':len(rows),'metrics':metrics,'paired':paired,'cases':details,
        'scope':'24 new stratified cases; original external gold; no relevance/action gold; not an official benchmark result; support is not approval'}
(out/'audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
