"""Four requests maximum, identical consumer/prompt rules; retrieval is sole variable."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/glm-01';out.mkdir(parents=True,exist_ok=False)
 shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
 shutil.copytree(b/'inputs',out/'inputs');shutil.copyfile(__file__,out/'run.py')
 protocol={'model':'glm-5.3-flash','consumer':'passage_cli; existing base legacy prompt, Spanish answers','response_format':'omitted','max_calls':4,'max_tokens':8192,'temperature':0,'source_budget':160000,'retrieval_budget':12000,'top_k':3,'prompt_budget':200000,'socket_seconds':90,'process_seconds':110,'retries':0,'stop':'transport, access, config or integrity failure','semantics':'producer criteria; fidelity not inferred from acceptance','cost':'include all calls; local extraction and lexical scan have no LLM calls; scan reads entire file'}
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 frozen={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'freeze.json').write_text(json.dumps(frozen,indent=2)+'\n')
 env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1');rows=[]
 for i,c in enumerate(json.loads((out/'inputs/cases.json').read_text())):
  for mode in (('source','retrieve') if i==0 else ('retrieve','source')):
   assert all(sha(out/n)==h for n,h in frozen.items())
   file=out/'inputs/source.txt';dest=out/c['id']/mode
   cmd=[sys.executable,'-m','agora.passage_cli','--source',str(file),'--source-id','qasper:1810.13414','--sha256',sha(file),'--question',c['question'],'--mode',mode,'--content-budget',str(160000 if mode=='source' else 12000),'--prompt-budget','200000','--top-k','3','--model','glm-5.3-flash','--max-output-tokens','8192','--out',str(dest)]
   start=time.monotonic()
   try:r=subprocess.run(cmd,env=env,timeout=110);code=r.returncode
   except subprocess.TimeoutExpired:code=None
   file=dest/'result.json';data=json.loads(file.read_text()) if file.exists() else {}
   row={'case':c['id'],'mode':mode,'seconds':round(time.monotonic()-start,3),'exit_code':code,'status':data.get('execution_status','unknown'),'diagnostic':data.get('diagnostic'),'tokens':data.get('response',{}).get('usage',{}).get('total_tokens'),'sha256':sha(file) if file.exists() else None};rows.append(row)
   (out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
   if not data or data.get('execution_status')=='failed':return 2
 assert all(sha(out/n)==h for n,h in frozen.items());return 0
if __name__=='__main__':raise SystemExit(main())
