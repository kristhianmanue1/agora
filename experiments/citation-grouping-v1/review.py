import json,hashlib,sys,subprocess,time
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];old=B.parent/'rubric-candidates-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=load(B/'freeze.json');candidate=B/'runs-generation/candidate.json';c=load(candidate)
assert c['execution_status']=='complete';assert sha(old/'inputs/source.txt')==f['source_sha256'] and sha(old/'rubric.json')==f['rubric_sha256']
receipt=B/'review-freeze.json'
with receipt.open('x') as handle:json.dump(dict(candidate_sha256=sha(candidate),response_sha256=sha(B/'runs-generation/response.json'),rubric_sha256=f['rubric_sha256'],expected=f['expected'],max_calls=1),handle,indent=2)
cli=[sys.executable,str(R/'scripts/agora_issues.py'),'--workspace',str(B/'inputs/workspace')];subprocess.run(cli+['init'],check=True);start=time.monotonic()
r=subprocess.run(cli+['review-rubric','--source',str(old/'inputs/source.txt'),'--source-sha256',f['source_sha256'],'--candidate',str(candidate),'--candidate-sha256',sha(candidate),'--part-id','P1','--question',f['question'],'--rubric',str(old/'rubric.json'),'--rubric-sha256',f['rubric_sha256'],'--live','--out',str(B/'runs-review')])
(B/'inputs/review-receipt.json').write_text(json.dumps(dict(exit_code=r.returncode,elapsed_seconds=round(time.monotonic()-start,3)),indent=2)+'\n')
