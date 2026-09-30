import json,hashlib,sys,subprocess,time
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];old=B.parent/'rubric-candidates-v1';f=json.loads((B/'freeze.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(old/'inputs/source.txt')==f['source_sha256'] and sha(old/'rubric.json')==f['rubric_sha256']
for c in f['cases']:assert sha(B/c['candidate'])==c['sha256']
cli=[sys.executable,str(R/'scripts/agora_issues.py'),'--workspace',str(B/'inputs/workspace')];subprocess.run(cli+['init'],check=True);receipts=[]
for c in f['cases']:
 start=time.monotonic();p=subprocess.run(cli+['review-rubric','--source',str(old/'inputs/source.txt'),'--source-sha256',f['source_sha256'],'--candidate',str(B/c['candidate']),'--candidate-sha256',c['sha256'],'--part-id','P1','--question',f['question'],'--rubric',str(old/'rubric.json'),'--rubric-sha256',f['rubric_sha256'],'--live','--out',str(B/('runs-'+c['id']))]);receipts.append(dict(id=c['id'],exit_code=p.returncode,elapsed_seconds=round(time.monotonic()-start,3)));(B/'inputs/receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
