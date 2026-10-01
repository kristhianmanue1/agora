"""One public fidelity-CLI call on fixed synthetic scope controls."""
import json,subprocess,sys,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((B/'temporal-freeze.json').read_text());assert sha(Path(__file__))==f['runner_sha256'];assert sha(B/'temporal-candidate.json')==f['candidate_sha256']
(B/'runs').mkdir()
cmd=[sys.executable,str(R.parent/'llavero/llavero.py'),'ejecutar','agora.dev.typesafe','--',sys.executable,str(R/'scripts/agora_issues.py'),'--workspace',str(R/'experiments/scoped-generalization-v1/inputs/workspace-fixed'),'review-fidelity','--candidate',str(B/'temporal-candidate.json'),'--candidate-sha256',f['candidate_sha256'],'--live','--out',str(B/'runs/temporal')]
subprocess.run(cmd,check=True)
