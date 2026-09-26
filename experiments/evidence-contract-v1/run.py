"""Fixed-version evaluation: one legacy regression and five evidence-contract calls."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/glm-01';out.mkdir(parents=True,exist_ok=False)
 shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
 shutil.copytree(b/'inputs',out/'inputs');shutil.copyfile(__file__,out/'run.py')
 protocol={'max_calls':6,'model':'glm-5.3-flash','temperature':0,'max_tokens':8192,'socket_seconds':180,'process_seconds':200,'retries':0,'stop':'transport, access or integrity failure; keep all format rejections','known_case':'G1 sufficient-context control; legacy prompt regression plus new claim/evidence contract','new_cases':'N1-N4 synthetic producer-defined, not independent holdout','promotion':'none; evaluate explicit contract, not NLI guarantee','cost':'all attempts included; no LLM retrieval/extraction calls','policies':{'max_quotes_per_part':12,'max_quote_bytes_per_part':12000,'max_quote_bytes_total':48000}}
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 manifest={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'freeze.json').write_text(json.dumps(manifest,indent=2)+'\n')
 cases=json.loads((out/'inputs/cases.json').read_text());jobs=[('legacy',cases[0])]+[('evidence',c) for c in cases]
 env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1');rows=[]
 for kind,c in jobs:
  assert all(sha(out/n)==h for n,h in manifest.items())
  source=out/'inputs'/c['source'];dest=out/kind/c['id']
  cmd=[sys.executable,'-m','agora.passage_cli' if kind=='legacy' else 'agora.evidence_cli','--source',str(source),'--source-id',c['id'],'--sha256',sha(source),'--question',c['question'],'--content-budget','12000','--prompt-budget','200000','--model','glm-5.3-flash','--max-output-tokens','8192','--timeout-seconds','180','--out',str(dest)]
  if kind=='legacy':cmd+=['--mode','reference']
  else:cmd+=['--aspects',str(out/'inputs'/c['aspects'])]
  if c.get('selection'):
   for s,e in json.loads((out/'inputs'/c['selection']).read_text())['ranges']:cmd+=['--range',f'{s}:{e}']
  start=time.monotonic()
  try:p=subprocess.run(cmd,env=env,timeout=200);code=p.returncode
  except subprocess.TimeoutExpired:code=None
  f=dest/'result.json';r=json.loads(f.read_text()) if f.exists() else {}
  row={'kind':kind,'case':c['id'],'seconds':round(time.monotonic()-start,3),'exit_code':code,'status':r.get('execution_status','unknown'),'diagnostic':r.get('diagnostic',r.get('diagnostics')),'tokens':r.get('response',{}).get('usage',{}).get('total_tokens'),'sha256':sha(f) if f.exists() else None};rows.append(row)
  (out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
  if not r or r.get('execution_status')=='failed':return 2
 assert all(sha(out/n)==h for n,h in manifest.items());return 0
if __name__=='__main__':raise SystemExit(main())
