import json,hashlib,sys,copy,shutil
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'));sys.path.insert(0,str(B.parent/'condition-expansion-v1'))
from expansion import expand
from agora.subquestions import prepare_subquestions
from agora.source import FileSourceAdapter
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();dump=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');f=load(B/'freeze.json');case=f['cases'][0];source=B/'inputs/case-1.txt';assert sha(source)==case['source_sha256']
plan=prepare_subquestions(FileSourceAdapter(source,'qasper:'+case['document_id']),case['source_sha256'],dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='P1',query=case['question'],reference_ranges=[])]),budget=8000,top_k=4,strategy='paragraphs-equal');assert plan['envelope'];initial=[[s['start_byte'],s['end_byte']] for s in plan['envelope']['spans']];expanded=expand(source.read_bytes(),case['question'],initial,10000,2);dump(B/'inputs/initial-plan.json',plan);dump(B/'inputs/expansion.json',expanded)
f['cases']=[]
for arm,ranges,size in [('initial',initial,plan['delivered_bytes']),('expanded',expanded['ranges'],expanded['delivered_bytes'])]:
 c=copy.deepcopy(case);c.update(id=arm,ranges=ranges,reading_bytes=size);f['cases'].append(c);shutil.copyfile(source,B/'inputs'/f'{arm}.txt');shutil.copyfile(B/'case-1-rubric.json',B/f'{arm}-rubric.json')
f.update(selector_sha256=sha(B.parent/'condition-expansion-v1/expansion.py'),expansion_sha256=sha(B/'inputs/expansion.json'),initial_plan_sha256=sha(B/'inputs/initial-plan.json'),scope='First hash-ranked eligible new local document, selected before expansion or provider output; initial versus frozen heuristic expansion. No source-based tuning or case substitution.',stop_rule='No retries, repairs, rubric changes or heuristic tuning. If contexts identical, run initial only and report no expansion benefit measured. Failed arms retained.')
if expanded['ranges']==initial:f['cases']=f['cases'][:1]
dump(B/'freeze.json',f)
base=b'Datasets Alpha and Beta.';controls=[dict(id='no_exception',source=base+b'\n\nDatasets contain labeled reviews.',budget=1000,expected_added=False),dict(id='positive_exception',source=base+b'\n\nDataset Beta is excluded in setting X.',budget=1000,expected_added=True),dict(id='insufficient_budget',source=base+b'\n\nDataset Beta is excluded in setting X.',budget=len(base),expected_added=False),dict(id='irrelevant_only',source=base+b'\n\nDataset documentation uses only blue font.',budget=1000,expected_added=False)]
results=[]
for x in controls:
 report=expand(x['source'],'Which datasets?',[[0,len(base)]],x['budget'],2);results.append(dict(id=x['id'],source=x['source'].decode(),expected_added=x['expected_added'],actual_added=bool(report['added']),matches=bool(report['added'])==x['expected_added'],report=report))
dump(B/'controls.json',dict(origin='Producer-defined synthetic controls; expectations concern task relevance, not merely regex matches',results=results));print('Reading:',[(c['id'],c['reading_bytes']) for c in f['cases']]);print('Controls:',[(r['id'],r['matches']) for r in results])
