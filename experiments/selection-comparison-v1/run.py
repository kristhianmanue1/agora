"""Offline lexical comparison; manual references are used only after retrieval."""
import argparse,hashlib,json,sys,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
sys.path.insert(0,str(args.repo/'src'))
from agora.source import FileSourceAdapter,digest
from agora.subquestions import prepare_subquestions
freeze=json.loads(Path(__file__).with_name('freeze.json').read_text())
raw=args.source.read_bytes();assert digest(raw)==freeze['source_sha256']
manual_raw=(args.repo/'experiments/explicit-plan-v1/plan.json').read_bytes();assert digest(manual_raw)==freeze['manual_plan_sha256'];manual=json.loads(manual_raw)
refs=manual['ranges'];reference_bytes=sum(b-a for a,b in refs)
def score(ranges):
 covered=[sum(max(0,min(b,d)-max(a,c)) for c,d in ranges) for a,b in refs]
 return dict(reference_covered_bytes=sum(covered),reference_total_bytes=reference_bytes,fully_covered_paragraphs=sum(n==b-a for n,(a,b) in zip(covered,refs)),paragraph_coverage=[dict(index=i,covered_bytes=n,total_bytes=b-a,complete=n==b-a) for i,(n,(a,b)) in enumerate(zip(covered,refs))])
assert score(refs)['fully_covered_paragraphs']==4
assert score([])['reference_covered_bytes']==0
args.out.mkdir(exist_ok=False);rows=[]
adapter=FileSourceAdapter(args.source,manual['source_id'])
for condition in freeze['conditions']:
 spec=dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='P1',query=condition['query'],reference_ranges=[])])
 start=time.monotonic();plan=prepare_subquestions(adapter,freeze['source_sha256'],spec,condition['budget'],condition['top_k']);seconds=time.monotonic()-start
 spans=(plan['envelope'] or {}).get('spans',[]);ranges=[(s['start_byte'],s['end_byte']) for s in spans]
 for s in spans:assert raw[s['start_byte']:s['end_byte']].decode()==s['text']
 measured=score(ranges);delivered=plan['delivered_bytes'];assert delivered<=condition['budget'];assert plan['provider_calls']==0
 row=dict(condition,**measured,delivered_bytes=delivered,bytes_outside_manual_reference=delivered-measured['reference_covered_bytes'],selected_ranges=ranges,seconds=seconds,provider_calls=0,source_scanned_bytes=len(raw))
 rows.append(row)
 (args.out/(condition['id']+'-plan.json')).write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
result=dict(schema='aria/selection-comparison/v1',conditions=rows,http_attempts=0,manual_reference_bytes=reference_bytes,reference_basis='producer-selected paragraphs, not exhaustive ground truth',positive_control='manual ranges recover 4/4',negative_control='empty ranges recover 0/4',source_sha256=freeze['source_sha256'],code_hashes={n:digest((args.repo/'src/agora'/n).read_bytes()) for n in ['passages.py','subquestions.py','source.py']})
(args.out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
for r in rows:print(r['id'],r['fully_covered_paragraphs'],r['delivered_bytes'],r['reference_covered_bytes'])
