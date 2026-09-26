"""Verify projection lineage and replay local checks; no provider calls."""
from pathlib import Path
import hashlib,json
from agora.evidence_review import review_evidence
b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/projected-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((out/'freeze.json').read_text());assert all(sha(out/n)==h for n,h in frozen.items())
for p in (out/'code/agora').glob('*.py'):assert sha(p)==sha(root/'src/agora'/p.name)
c=json.loads((out/'candidate.json').read_text());o=json.loads((out/'original.json').read_text());r=json.loads((out/'review.json').read_text());row=json.loads((out/'execution.json').read_text())
assert sha(out/'review.json')==row['sha256']
assert c['diagnostic_projection']['original_file_sha256']==sha(b/'runs/glm-01/inputs/R-regression.json')
assert o==json.loads((b/'runs/glm-01/inputs/R-regression.json').read_text())
assert c['parts'][0]['claims']==[o['parts'][0]['claims'][2]]
source=(root/'experiments/evidence-review-v1/runs/glm-01/inputs/N2.txt').read_bytes();assert hashlib.sha256(source).hexdigest()==c['source_sha256']
for a in c['citations']:assert all(source[m['start_byte']:m['end_byte']].decode()==a['quote'] for m in a['matches'])
replay=review_evidence(c,lambda s,u:r['response'],response_language='es',review_version='v2')
for key in ('schema','candidate_sha256','execution_status','assessment','recommendation','diagnostics'):assert replay.get(key)==r.get(key),key
claims=r.get('assessment',{}).get('claims',[]);passed=bool(claims) and claims[0]['support']=='insufficient'
report=dict(row,freeze_current_code_lineage_and_replay_verified=True,known_regression_detected=passed,assessment=r.get('assessment'),scope='isolated known claim only; full review remains failed')
(out/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
