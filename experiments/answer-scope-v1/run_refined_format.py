"""Four refined producer-known development cases; one request each, no retries."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/glm-03';out.mkdir(parents=True,exist_ok=False)
 shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
 shutil.copytree(b/'inputs/refined',out/'inputs');shutil.copyfile(__file__,out/'run.py')
 protocol={'model':'glm-5.3-flash','profile':'concise-v1','max_calls':4,'max_output_tokens':8192,'temperature':0,'socket_seconds':90,'process_seconds':110,'retries':0,'holdout':False,'purpose':'development; not QASPER re-evaluation','stop':'non-timeout operational failure'}
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 manifest={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'freeze.json').write_text(json.dumps(manifest,indent=2)+'\n')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(out/'code'));rows=[]
 for c in json.loads((out/'inputs/cases.json').read_text()):
  assert all(sha(out/n)==h for n,h in manifest.items())
  source=out/'inputs'/c['source'];cmd=[sys.executable,'-m','agora.routed_cli','--source',str(source),'--source-id',c['id'],'--sha256',sha(source),'--question',c['question'],'--parts',str(out/'inputs'/c['parts']),'--response-language',c['language'],'--answer-profile','concise-v1','--model','glm-5.3-flash','--out',str(out/c['id'])]
  start=time.monotonic()
  try:p=subprocess.run(cmd,env=env,timeout=110);code=p.returncode
  except subprocess.TimeoutExpired:code=None
  f=out/c['id']/'result.json';r=json.loads(f.read_text()) if f.exists() else {}
  row={'case':c['id'],'seconds':round(time.monotonic()-start,3),'exit_code':code,'status':r.get('execution_status','unknown'),'diagnostic':r.get('diagnostic'),'result_sha256':sha(f) if f.exists() else None,'tokens':r.get('response',{}).get('usage',{}).get('total_tokens')};rows.append(row)
  (out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
  if r and r.get('execution_status')!='complete' and r.get('diagnostic')!='timeout':break
 assert all(sha(out/n)==h for n,h in manifest.items())
 return 0 if len(rows)==4 else 2
if __name__=='__main__':raise SystemExit(main())
