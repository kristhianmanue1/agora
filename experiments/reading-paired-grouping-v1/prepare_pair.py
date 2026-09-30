import json,hashlib,sys,copy,shutil
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.subquestions import prepare_subquestions
from agora.source import FileSourceAdapter
load=lambda p:json.loads(p.read_text());dump=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');f=load(B/'freeze.json');case=f['cases'][0];source=B/'inputs/case-1.txt'
# Question only: no annotations, requirements or reference ranges used for retrieval.
spec=dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='P1',query=case['question'],reference_ranges=[])])
plan=prepare_subquestions(FileSourceAdapter(source,'qasper:'+case['document_id']),case['source_sha256'],spec,budget=8000,top_k=4,strategy='paragraphs-equal');dump(B/'inputs/selection-plan.json',plan);assert plan['envelope']
f['cases']=[]
for arm in ('selected','full'):
 c=copy.deepcopy(case);c['id']=arm;c['ranges']=[[s['start_byte'],s['end_byte']] for s in plan['envelope']['spans']] if arm=='selected' else [[0,case['source_bytes']]];c['reading_bytes']=plan['delivered_bytes'] if arm=='selected' else case['source_bytes'];f['cases'].append(c);shutil.copyfile(source,B/'inputs'/f'{arm}.txt');shutil.copyfile(B/'case-1-rubric.json',B/f'{arm}-rubric.json')
f['comparison']='One newly selected source, two original candidates; full vs question-only lexical selection. No oracle reference ranges. Local retriever scans full source; savings refer to model input, not storage I/O.';f['selection_plan_sha256']=hashlib.sha256((B/'inputs/selection-plan.json').read_bytes()).hexdigest();f['stop_rule']='No retry, repair, case replacement or rubric changes. Failed arms remain failed; successful arms reviewed separately. No default promotion.';dump(B/'freeze.json',f)
print('Reading bytes:',[(c['id'],c['reading_bytes']) for c in f['cases']])
