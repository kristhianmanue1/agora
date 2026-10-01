"""Post-integration check: current product baseline, not the historical comparator."""
import json,sys,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.structured_plan import prepare
from agora.source import FileSourceAdapter,digest
from agora.subquestions import prepare_subquestions
from agora.fidelity_cli import request,assess
load=lambda p:json.loads(p.read_text());data=load(R/'experiments/qasper-v1/inputs/test.json');f=load(B/'freeze.json');rows=[]
for c in f['cases']:
 p=data[c['document_id']];structure={k:p[k] for k in ('title','abstract','full_text')};source=R/c['source_path'];assert digest(source.read_bytes())==c['source_sha256']
 spec=dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='P1',query=c['question'],reference_ranges=[])])
 adapter=FileSourceAdapter(source,c['document_id']);base=prepare_subquestions(adapter,c['source_sha256'],spec,20000,3);plan=prepare(adapter,c['source_sha256'],spec,structure,20000,3)
 spans=plan['envelope']['spans'];assert all(any(t['start_byte']<=s['start_byte'] and s['end_byte']<=t['end_byte'] for t in spans) for s in base['envelope']['spans']);assert plan['delivered_bytes']<=20000
 rubric=R/c['rubric_path'];assert digest(rubric.read_bytes())==c['rubric_sha256'];refs={(x['evidence']['start_byte'],x['evidence']['end_byte']) for x in load(rubric)['requirements']}
 def score(ss):return sum(any(s['start_byte']<=a and b<=s['end_byte'] for s in ss) for a,b in refs)
 rows.append(dict(id=c['id'],baseline=score(base['envelope']['spans']),structured=score(spans),references=len(refs),bytes=plan['delivered_bytes']))
tf=load(B/'temporal-freeze.json');candidate=load(B/'temporal-candidate.json');saved=load(B/'runs/temporal/result.json');assert digest((B/'temporal-candidate.json').read_bytes())==tf['candidate_sha256'];assert request(candidate)==saved['request'];assert assess(saved['response'],saved['request'])==saved['label']
labels={k:v['choice'] for k,v in saved['response']['answers'].items()}
report=dict(rows=rows,baseline_ranges_preserved=True,provider_calls=0,scope='Known development cases, current product baseline top-k 3, 20000 bytes; range recall is not semantic accuracy',temporal=dict(expected=tf['expected'],observed=labels,matches=sum(labels[k]==v for k,v in tf['expected'].items()),controls=len(labels),http_calls=saved['http_attempts'],tokens=sum(saved['response']['usage'].values()),independent_adjudication=False),implementation_hashes={n:digest((R/'src/agora'/n).read_bytes()) for n in ('structured_plan.py','structure_selection.py','plan_generation.py')})
if len(sys.argv)>1:
 with Path(sys.argv[1]).open('x') as h:json.dump(report,h,indent=2);h.write('\n')
print(json.dumps(report,indent=2))
