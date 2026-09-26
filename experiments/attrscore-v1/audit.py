"""Offline verification, replay and fixed-score comparison; never calls GLM."""
from pathlib import Path
import csv,hashlib,json
from agora.evidence_review import review_evidence
from score import classification_scores
b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/glm-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((out/'freeze.json').read_text());assert all(sha(out/n)==h for n,h in frozen.items())
for p in (out/'code/agora').glob('*.py'):assert sha(p)==sha(root/'src/agora'/p.name)
raw=list(csv.DictReader((out/'inputs/AttrEval-GenSearch.csv').open()));cases=json.loads((out/'inputs/pilot-01/cases.json').read_text());gold=json.loads((out/'inputs/pilot-01/gold.json').read_text());rows=json.loads((out/'execution.json').read_text())
expected={c['id']:gold[c['id']]['support'] for c in cases};predictions={v:{} for v in ('v1','v2')};details=[]
for case in cases:
 c=json.loads((out/'inputs/pilot-01'/case['candidate']).read_text());original=raw[case['source_row_index']]
 assert gold[case['id']]['label']==original['label']
 assert gold[case['id']]['support']=={'Attributable':'supported','Contradictory':'contradicted','Extrapolatory':'insufficient'}[original['label']]
 assert c['parts'][0]['claims'][0]['text']==original['answer'];assert c['parts'][0]['claims'][0]['quotes']==[original['reference']]
 source=(out/'inputs/pilot-01'/case['source']).read_bytes();assert source.decode()==original['reference'];assert hashlib.sha256(source).hexdigest()==c['source_sha256']
 for version in ('v1','v2'):
  f=out/version/case['id']/'result.json'
  if not f.exists():continue
  r=json.loads(f.read_text());row=next(x for x in rows if x['case']==case['id'] and x['version']==version);assert sha(f)==row['sha256']
  request=json.loads(f.with_name('request.json').read_text())
  assert request['messages']==[{'role':'system','content':r['prompt']['system']},{'role':'user','content':r['prompt']['user']}]
  sent=json.loads(r['prompt']['user']);assert sent['question']==(original['query'] or 'Assess whether the supplied reference supports the answer.');assert set(sent)=={'response_language','question','aspects','claims','missing'}
  assert sent['claims']==[{'part_id':'answer','claim_index':0,'text':original['answer'],'quotes':[original['reference']]}]
  replay=review_evidence(c,lambda s,u:r['response'],response_language='en',review_version=version)
  for key in ('schema','candidate_sha256','execution_status','assessment','diagnostics','recommendation'):assert replay.get(key)==r.get(key),(case['id'],version,key)
  prediction=r['assessment']['claims'][0]['support'] if r['execution_status']=='complete' else 'failed';predictions[version][case['id']]=prediction
  details.append({'case':case['id'],'version':version,'gold':expected[case['id']],'prediction':prediction,'correct':prediction==expected[case['id']],'status':r['execution_status'],'tokens':row['tokens'],'seconds':row['seconds'],'diagnostics':r.get('diagnostics')})
metrics={}
for version in predictions:
 selected=[x for x in rows if x['version']==version]
 metrics[version]=dict(classification_scores(expected,predictions[version]),calls=len(selected),tokens=sum(x['tokens'] or 0 for x in selected),unknown_usage=sum(x['tokens'] is None for x in selected),seconds=round(sum(x['seconds'] for x in selected),3))
paired={'both_correct':0,'v1_only_correct':0,'v2_only_correct':0,'neither_correct':0,'unpaired':0}
for cid,label in expected.items():
 if cid not in predictions['v1'] or cid not in predictions['v2']:paired['unpaired']+=1;continue
 a=predictions['v1'][cid]==label;b2=predictions['v2'][cid]==label
 paired['both_correct' if a and b2 else 'v1_only_correct' if a else 'v2_only_correct' if b2 else 'neither_correct']+=1
report={'analysis_code_hashes':{n:sha(b/n) for n in ('score.py','audit.py')},'freeze_current_code_input_and_replay_verified':True,'calls':len(rows),'metrics':metrics,'paired':paired,'cases':details,'scope':'balanced 12-case development pilot; no official full-dataset result; no independent adjudication of disagreements'}
(out/'audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
