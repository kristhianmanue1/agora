import json,hashlib,random,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=R/'experiments/reviewer-separated-v1';P=R/'experiments/reviewer-scopes-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B.mkdir();(B/'inputs').mkdir();(B/'.gitignore').write_text('inputs/\nruns-*/\n');original=load(P/'inputs/cases.json');assert sha(P/'inputs/cases.json')==load(P/'freeze.json')['cases_sha256'];keys=load(P/'key.json');clarity={};reviews=[];mapping=[]
for c in original:
 tid='t'+hashlib.sha256(c['task'].encode()).hexdigest()[:12];clarity[tid]=dict(id=tid,axis='interpretation',state={'task':c['task']})
 for axis in ('fidelity','coverage'):
  cid='r'+hashlib.sha256((c['id']+axis).encode()).hexdigest()[:12];state=dict(task=c['task'],answer=c['answer']);state['delivered_passages' if axis=='fidelity' else 'full_source']=c['delivered_passages' if axis=='fidelity' else 'full_source'];reviews.append(dict(id=cid,axis=axis,state=state));mapping.append(dict(id=cid,original_id=c['id'],task_id=tid,axis=axis))
random.Random('split-review-v1').shuffle(reviews)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
for phase,cases in [('clarity',list(clarity.values())),('review',reviews)]:
 p=B/'inputs'/phase;p.mkdir();dump(p/'cases.json',cases)
dump(B/'key.json',dict(original_keys=keys,mapping=mapping));dump(B/'freeze.json',dict(code_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),phase_hashes={phase:sha(B/'inputs'/phase/'cases.json') for phase in ('clarity','review')},original_result_sha256=sha(P/'result.json'),max_calls=len(clarity)+len(reviews),timeout_seconds=90,retries=0,model='jev-1.13.0',selection='Same ten candidates as explicit-scopes experiment; no new generation',aggregation='If task interpretation is not clear, final disposition requires_clarification regardless of raw coverage. Raw reviews remain unchanged. Otherwise retain separate fidelity and coverage without automatic acceptance.',limits='Development cases, producer expectations, one draw; historical comparison is confounded by prompt and time; no product activation'))
print('Prepared',len(clarity),'question-only checks and',len(reviews),'isolated reviews')
