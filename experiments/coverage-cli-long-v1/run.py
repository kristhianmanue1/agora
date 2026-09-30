import json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];f=json.loads((B/'freeze.json').read_text())
for c in f['candidates']:
 cmd=['/usr/bin/python3',str(R.parent/'llavero/llavero.py'),'ejecutar','zai','--','/usr/bin/python3',str(R/'scripts/agora_issues.py'),'--workspace',str(B/'inputs/workspace'),'review-coverage','--source',str(B/'inputs/source.txt'),'--source-sha256',f['source_sha256'],'--candidate',str(B/'inputs'/f"{c['method']}.json"),'--candidate-sha256',c['candidate_sha256'],'--part-id','P1','--question',c['question'],'--live','--out',str(B/f"runs-{c['method']}")]
 result=subprocess.run(cmd)
 if result.returncode:raise SystemExit(result.returncode)
