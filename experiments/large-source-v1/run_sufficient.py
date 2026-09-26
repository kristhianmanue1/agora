"""Two new G1 calls, same question and consumer, revised timeout for both."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/sufficient-01'
 assert not (out/'freeze.json').exists()
 old=b/'runs/glm-01';frozen_old=json.loads((old/'freeze.json').read_text())
 assert all(sha(old/n)==h for n,h in frozen_old.items())
 for n,h in frozen_old.items():
  if n.startswith('code/agora/'):assert sha(root/'src/agora'/n.removeprefix('code/agora/'))==h
 shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
 shutil.copytree(b/'inputs',out/'inputs')
 for name in ('run_sufficient.py',):shutil.copyfile(b/name,out/name)
 protocol={'max_calls':1,'model':'glm-5.3-flash','max_tokens':8192,'temperature':0,'socket_seconds':180,'process_seconds':200,'retries':0,'source_budget':160000,'retrieval_budget':12000,'prompt_budget':200000,'response_format':'omitted','case':'G1; previously observed development case','stop':'transport/access/config/integrity failure','criteria':'unchanged from glm-01; semantic review required','method':'producer selected reference-informed sufficient context; not retrieval evaluation'}
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 frozen={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'freeze.json').write_text(json.dumps(frozen,indent=2)+'\n')
 env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1');rows=[]
 question=json.loads((out/'inputs/cases.json').read_text())[1]['question']
 for mode in ('reference',):
  assert all(sha(out/n)==h for n,h in frozen.items())
  source=out/'inputs/source.txt'
  cmd=[sys.executable,'-m','agora.passage_cli','--source',str(source),'--source-id','qasper:1810.13414','--sha256',sha(source),'--question',question,'--mode',mode,'--content-budget',str(12000 if mode=='reference' else 160000),'--prompt-budget','200000','--model','glm-5.3-flash','--max-output-tokens','8192','--timeout-seconds','180','--out',str(out/'G1'/mode)]
  if mode=='reference':
   for s,e in json.loads((out/'selection.json').read_text())['ranges']:cmd+=['--range',f'{s}:{e}']
  start=time.monotonic()
  try:p=subprocess.run(cmd,env=env,timeout=200);code=p.returncode
  except subprocess.TimeoutExpired:code=None
  f=out/'G1'/mode/'result.json';r=json.loads(f.read_text()) if f.exists() else {}
  row={'case':'G1','mode':mode,'seconds':round(time.monotonic()-start,3),'exit_code':code,'status':r.get('execution_status','unknown'),'diagnostic':r.get('diagnostic'),'tokens':r.get('response',{}).get('usage',{}).get('total_tokens'),'sha256':sha(f) if f.exists() else None};rows.append(row)
  (out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
  if not r or r.get('execution_status')=='failed':return 2
 assert all(sha(out/n)==h for n,h in frozen.items());return 0
if __name__=='__main__':raise SystemExit(main())
