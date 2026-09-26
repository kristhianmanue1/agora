"""Offline replay and failure injection using recorded responses; no HTTP calls."""
from pathlib import Path
import copy,hashlib,json
from agora.review_batch import ReviewBudget,review_candidate,project,fingerprint
b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/glm-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((out/'freeze.json').read_text());assert all(sha(out/n)==h for n,h in frozen.items())
for p in (out/'code/agora').glob('*.py'):assert sha(p)==sha(root/'src/agora'/p.name)
c=json.loads((out/'candidate.json').read_text());r=json.loads((out/'result.json').read_text());rows=json.loads((out/'execution.json').read_text());source=(out/'source.txt').read_bytes()
assert hashlib.sha256(source).hexdigest()==c['source_sha256'];assert r['candidate_sha256']==fingerprint(c)
for a in c['citations']:assert all(source[m['start_byte']:m['end_byte']].decode()==a['quote'] for m in a['matches'])
receipts=[]
for row in rows:
 f=out/'calls'/str(row['call']);assert sha(f/'request.json')==row['request_sha256']
 if row['response_sha256']:assert sha(f/'response.json')==row['response_sha256'];receipts.append(json.loads((f/'response.json').read_text()))
 else:receipts.append(None)
for j in r['jobs']:
 if j.get('projection_sha256'):assert fingerprint(project(c,j,r['candidate_sha256']))==j['projection_sha256']

def replay(budget=None,fail=None):
 counter=0
 def provider(s,u,**limits):
  nonlocal counter
  counter+=1;index=counter-1;wire=json.loads((out/'calls'/str(counter)/'request.json').read_text())
  assert wire['messages']==[{'role':'system','content':s},{'role':'user','content':u}]
  if (fail=='transport' and counter==2) or receipts[index] is None:raise RuntimeError('injected_or_recorded_transport_failure')
  receipt=copy.deepcopy(receipts[index])
  if fail=='length' and counter==3:receipt['finish_reason']='length'
  return receipt
 return review_candidate(c,provider,budget=budget,response_language='es',clock=lambda:0)

base=replay()
for field in ('candidate_sha256','jobs','ledger','reviewed_jobs','expected_jobs','review_coverage','execution_status','recommendation','findings','stop_reason'):assert r[field]==base[field],field
probes={}
if len(rows)==6 and all(receipts):
 for name,budget,fail in [('calls',ReviewBudget(max_calls=2),None),('output',ReviewBudget(max_output_tokens_total=8192),None),('truncated',None,'length'),('transport',None,'transport')]:
  p=replay(budget,fail);assert p['execution_status']=='incomplete';assert p['recommendation']=='review_incomplete';assert p['review_coverage']=='incomplete'
  probes[name]={k:p[k] for k in ('execution_status','review_coverage','reviewed_jobs','expected_jobs','ledger','stop_reason')}
  (out/('probe-'+name+'.json')).write_text(json.dumps(p,indent=2))
assessments={j['claim_index']:j['review']['assessment']['claims'][0] for j in r['jobs'] if j['status']=='reviewed' and j['kind']=='claim'}
checks={'six_claims_reviewed':r['reviewed_jobs']==6 and r['review_coverage']=='complete',
        'a1_c1_insufficient':assessments.get(2,{}).get('support')=='insufficient',
        'regression_detail_extra':assessments.get(5,{}).get('relevance')=='extra'}
report={'freeze_current_code_source_and_replay_verified':True,'result_sha256':sha(out/'result.json'),'checks':checks,
        'calls':len(rows),'known_tokens':sum(x['tokens'] or 0 for x in rows),'unknown_usage':sum(x['tokens'] is None for x in rows),
        'call_seconds':round(sum(x['seconds'] for x in rows),3),'batch_seconds':r['elapsed_seconds'],
        'ledger':r['ledger'],'probes':probes,'independent_adjudication':'not_performed'}
(out/'audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
