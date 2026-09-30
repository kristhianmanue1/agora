import json,hashlib,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];P=B.parent/'coverage-cli-long-v1';f=json.loads((P/'freeze.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(B/'.gitignore').write_text('runs-*/\n');freeze=B/'freeze.json'
if freeze.exists():raise SystemExit('Run already reserved; inspect journals, do not retry')
for method in ('equal','shared'):
 old=json.loads((B.parent/'omission-cli-v1'/f'runs-{method}/request.json').read_text())
 import sys
 sys.path.insert(0,str(R/'src'))
 from agora.omission_cli import SYSTEM
 assert old['system']==SYSTEM
freeze.write_text(json.dumps(dict(max_calls=2,retries=0,max_output_tokens=4096,timeout_seconds=90,expectations=dict(equal='two known limitations: BLEU diversity and embedding compositionality',shared='no material omission expected'),source_sha256=f['source_sha256'],module_sha256=sha(R/'src/agora/omission_cli.py'),origin='known public QASPER development pair; producer expectations, not independent'),indent=2)+'\n')
for c in f['candidates']:
 method=c['method'];review=P/f'runs-{method}/result.json';cmd=['/usr/bin/python3',str(R.parent/'llavero/llavero.py'),'ejecutar','zai','--','/usr/bin/python3',str(R/'scripts/agora_issues.py'),'--workspace',str(P/'inputs/workspace'),'diagnose-omissions','--source',str(P/'inputs/source.txt'),'--source-sha256',f['source_sha256'],'--candidate',str(P/'inputs'/f'{method}.json'),'--candidate-sha256',c['candidate_sha256'],'--part-id','P1','--question',c['question'],'--review',str(review),'--review-sha256',sha(review),'--live','--max-output-tokens','4096','--out',str(B/f'runs-{method}')]
 result=subprocess.run(cmd)
 if result.returncode:raise SystemExit(result.returncode)
