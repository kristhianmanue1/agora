"""One fresh diagnostic call on unchanged claim/citations; no retry of full review."""
from pathlib import Path
import copy,hashlib,json,os,shutil,subprocess,sys,time

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=Path(__file__).resolve().parent;root=b.parents[1];old=b/'runs/glm-01';out=b/'runs/projected-01';out.mkdir(parents=True,exist_ok=False)
shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'));shutil.copyfile(old/'worker.py',out/'worker.py');shutil.copyfile(__file__,out/'projected.py')
original=json.loads((old/'inputs/R-regression.json').read_text());candidate=copy.deepcopy(original)
candidate['parts']=[copy.deepcopy(original['parts'][0])];candidate['parts'][0]['claims']=[copy.deepcopy(original['parts'][0]['claims'][2])]
candidate['parts'][0].update(status='partial',missing=['Proyección diagnóstica de una afirmación; no es la respuesta completa.'])
candidate['citations']=[dict(a,claim_index=0) for a in original['citations'] if a['part_id']==original['parts'][0]['id'] and a['claim_index']==2]
candidate.update(answer_status='candidate_partial',review_queue=[{'part_id':original['parts'][0]['id'],'claim_index':0,'support':'not_verified'}],coverage_review=[{'part_id':original['parts'][0]['id'],'coverage':'not_verified','model_status':'not_applicable_diagnostic_projection'}])
candidate['diagnostic_projection']={'original_file_sha256':sha(old/'inputs/R-regression.json'),'original_part_id':original['parts'][0]['id'],'original_claim_index':2,'reason':'full six-claim review exceeded output budget; claim text and own quotes unchanged','scope':'diagnostic projection, not a new source answer'}
(out/'candidate.json').write_text(json.dumps(candidate,indent=2));(out/'original.json').write_text(json.dumps(original,indent=2))
protocol={'max_calls':1,'max_output_tokens':8192,'socket_seconds':180,'process_seconds':200,'model':'glm-5.3-flash','temperature':0,'retries':0,'expected':'claim0 support insufficient; A1-C1 absent from its quotes','scope':'known regression isolated; cannot stand in for full candidate review'}
(out/'protocol.json').write_text(json.dumps(protocol,indent=2));frozen={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'freeze.json').write_text(json.dumps(frozen,indent=2))
env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1');start=time.monotonic();dest=out/'review.json'
try:p=subprocess.run([sys.executable,str(out/'worker.py'),'--worker',str(out/'candidate.json'),str(dest)],env=env,timeout=200);code=p.returncode
except subprocess.TimeoutExpired:code=None
r=json.loads(dest.read_text()) if dest.exists() else {}
row={'status':r.get('execution_status','unknown'),'exit_code':code,'seconds':round(time.monotonic()-start,3),'tokens':r.get('response',{}).get('usage',{}).get('total_tokens'),'sha256':sha(dest) if dest.exists() else None,'diagnostics':r.get('diagnostics')};(out/'execution.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
assert all(sha(out/n)==h for n,h in frozen.items())
raise SystemExit(2 if not r or r.get('execution_status')=='failed' else 0)
