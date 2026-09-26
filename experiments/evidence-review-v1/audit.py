"""Offline artifact audit; does not adjudicate model judgments."""
from pathlib import Path
import hashlib,json
from agora.evidence_ids import build_units
b=Path(__file__).resolve().parent;out=b/'runs/glm-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((out/'freeze.json').read_text());assert all(sha(out/n)==h for n,h in freeze.items())
rows=json.loads((out/'execution.json').read_text());summaries=[]
for row in rows:
 p=out/row['path'];assert sha(p)==row['sha256'];r=json.loads(p.read_text())
 if row['kind']=='review':
  cpath=out/'inputs'/(row['case']+'.json') if row['case'].startswith('C-') else out/row['case']/'result.json'
  c=json.loads(cpath.read_text());assert r['candidate_sha256']==hashlib.sha256(json.dumps(c,sort_keys=True,ensure_ascii=True).encode()).hexdigest()
  summaries.append(dict(row,assessment=r.get('assessment'),recommendation=r.get('recommendation')));continue
 cid=row['case'].split('-')[0];source=(out/'inputs'/(cid+'.txt')).read_bytes()
 assert hashlib.sha256(source).hexdigest()==r['source_sha256']
 for span in r['envelope']['spans']:assert source[span['start_byte']:span['end_byte']].decode()==span['text']
 units=build_units(r['envelope'],r['source_id'],r['source_sha256'],r['max_unit_bytes']);assert units==r['evidence_units']
 byid={u['id']:u for u in units};size=0
 for a in r.get('citations',[]):
  unit=byid[a['evidence_id']];assert a['quote']==unit['text'];assert a['matches']==[{'start_byte':unit['start_byte'],'end_byte':unit['end_byte']}]
  assert source[unit['start_byte']:unit['end_byte']].decode()==a['quote'];size+=len(a['quote'].encode())
 summaries.append(dict(row,quoted_bytes=size,citations=len(r.get('citations',[])),units=len(units),claims=sum(len(p['claims']) for p in r.get('parts',[]))))
report={'freeze_verified':True,'calls':len(rows),'known_tokens':sum(r['tokens'] or 0 for r in rows),'unknown_usage':sum(r['tokens'] is None for r in rows),'seconds':round(sum(r['seconds'] for r in rows),3),'rows':summaries,'semantic_adjudication':'not_performed'}
(out/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
