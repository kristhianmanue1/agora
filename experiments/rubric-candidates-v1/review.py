"""Run the public CLI twice, with predeclared candidate hashes and labels hidden."""
import json,hashlib,sys,subprocess,time
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1]
f=json.loads((B/'freeze.json').read_text());review=json.loads((B/'review-freeze.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(B/'rubric.json')==f['rubric_sha256'];assert sha(B/'inputs/source.txt')==f['source_sha256']
for c in review['cases']:assert sha(B/c['candidate'])==c['sha256']
workspace=B/'inputs/workspace';cli=[sys.executable,str(R/'scripts/agora_issues.py'),'--workspace',str(workspace)]
subprocess.run(cli+['init'],check=True)
receipts=[]
for c in review['cases']:
 start=time.monotonic()
 result=subprocess.run(cli+['review-rubric','--source',str(B/'inputs/source.txt'),'--source-sha256',f['source_sha256'],'--candidate',str(B/c['candidate']),'--candidate-sha256',c['sha256'],'--part-id','P1','--question',f['question'],'--rubric',str(B/'rubric.json'),'--rubric-sha256',f['rubric_sha256'],'--live','--out',str(B/('runs-'+c['id']))])
 receipts.append(dict(id=c['id'],exit_code=result.returncode,elapsed_seconds=round(time.monotonic()-start,3)))
 (B/'inputs/review-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
