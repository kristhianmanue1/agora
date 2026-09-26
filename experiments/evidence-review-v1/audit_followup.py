"""Audit fresh follow-up and its predefined control outcomes, without model calls."""
from pathlib import Path
import hashlib,json
b=Path(__file__).resolve().parent;out=b/'runs/format-02';root=b.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((out/'freeze.json').read_text());assert all(sha(out/n)==h for n,h in frozen.items())
for p in (out/'code/agora').glob('*.py'):assert sha(p)==sha(root/'src/agora'/p.name)
rows=json.loads((out/'execution.json').read_text());details=[]
for row in rows:
 p=out/(row['case']+'-review.json');assert sha(p)==row['sha256'];r=json.loads(p.read_text());c=json.loads((out/(row['case']+'.json')).read_text())
 assert r['candidate_sha256']==hashlib.sha256(json.dumps(c,sort_keys=True,ensure_ascii=True).encode()).hexdigest()
 details.append(dict(row,assessment=r.get('assessment'),recommendation=r.get('recommendation')))
by_case={r['case']:r for r in details}
checks={
 'language_mismatch_detected':by_case['C-language'].get('assessment',{}).get('language')=='mismatch',
 'support_control_labels_match':[x['support'] for x in by_case['C-support'].get('assessment',{}).get('claims',[])]==['supported','insufficient','contradicted'],
 'real_missing_qualifier_flagged':any(x['claim_index']==2 and x['support']=='insufficient' for x in by_case['N2-1024'].get('assessment',{}).get('claims',[]))}
report={'predefined_checks':checks,'freeze_and_current_code_verified':True,'calls':len(rows),'known_tokens':sum(x['tokens'] or 0 for x in rows),'unknown_usage':sum(x['tokens'] is None for x in rows),'seconds':round(sum(x['seconds'] for x in rows),3),'rows':details,'scope':'known development controls; not independent adjudication'}
(out/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
