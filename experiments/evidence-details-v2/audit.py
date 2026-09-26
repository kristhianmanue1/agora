"""Replay local v2 validation and predefined expectations, never provider calls."""
from pathlib import Path
import hashlib,json
from agora.evidence_review import review_evidence
b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/glm-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((out/'freeze.json').read_text());assert all(sha(out/n)==h for n,h in frozen.items())
for p in (out/'code/agora').glob('*.py'):assert sha(p)==sha(root/'src/agora'/p.name)
rows=json.loads((out/'execution.json').read_text());cases={c['id']:c for c in json.loads((out/'inputs/cases.json').read_text())};audited=[]
for row in rows:
 cid=row['case'];p=out/(cid+'-review.json');assert sha(p)==row['sha256'];r=json.loads(p.read_text());c=json.loads((out/'inputs'/(cid+'.json')).read_text())
 source=(root/'experiments/evidence-review-v1/runs/glm-01/inputs/N2.txt' if cid=='R-regression' else out/'inputs'/(cid+'.txt')).read_bytes()
 assert hashlib.sha256(source).hexdigest()==c['source_sha256']
 for a in c['citations']:
  assert all(source[m['start_byte']:m['end_byte']].decode()==a['quote'] for m in a['matches'])
 replay=review_evidence(c,lambda s,u:r['response'],response_language='es',review_version='v2')
 for key in ('schema','candidate_sha256','execution_status','assessment','recommendation','diagnostics'):
  assert replay.get(key)==r.get(key),(cid,key)
 expectations=cases[cid];claims={str(x['claim_index']):x for x in r.get('assessment',{}).get('claims',[])}
 checks=[{'claim_index':int(i),'property':'support','expected':s,'observed':claims.get(i,{}).get('support'),'passed':claims.get(i,{}).get('support')==s} for i,s in expectations['expected_support'].items()]
 checks += [{'claim_index':int(i),'property':'relevance','expected':s,'observed':claims.get(i,{}).get('relevance'),'passed':claims.get(i,{}).get('relevance')==s} for i,s in expectations.get('expected_relevance',{}).items()]
 audited.append(dict(row,checks=checks,all_expected_passed=all(c['passed'] for c in checks),details=sum(len(c['details']) for c in claims.values()),assessment=r.get('assessment')))
report={'freeze_current_code_and_replay_verified':True,'calls':len(rows),'expected_cases':len(cases),'known_tokens':sum(x['tokens'] or 0 for x in rows),'unknown_usage':sum(x['tokens'] is None for x in rows),'seconds':round(sum(x['seconds'] for x in rows),3),'cases_passed':sum(x['all_expected_passed'] for x in audited),'checks_passed':sum(c['passed'] for x in audited for c in x['checks']),'checks_total':sum(len(x['checks']) for x in audited),'rows':audited,'independent_adjudication':'not_performed'}
(out/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
