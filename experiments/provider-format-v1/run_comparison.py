"""Paired format-only comparison on eight known development fixtures."""
import hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/paired-01';out.mkdir(parents=True,exist_ok=False)
 shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
 shutil.copytree(root/'experiments/answer-scope-v1/inputs/final',out/'inputs')
 shutil.copyfile(__file__,out/'run.py')
 protocol={'model':'glm-5.3-flash','profile':'concise-v1','modes':['default','json_object'],'max_calls':16,'max_output_tokens':8192,'temperature':0,'socket_seconds':90,'process_seconds':110,'retries':0,'holdout':False,'order':'alternate per case','purpose':'format-only development comparison; no QASPER claims','expected_status':{'E1':'not_in_document','E2':'not_in_document','E3':'not_in_document','E4':'not_in_document','D2':'answer','D4':'answer','D6':'answer','D8':'answer'},'stop':'transport/access/config/integrity failure; record and continue format rejection'}
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 frozen={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'freeze.json').write_text(json.dumps(frozen,indent=2)+'\n')
 rows=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(out/'code'))
 for i,c in enumerate(json.loads((out/'inputs/cases.json').read_text())):
  for mode in (protocol['modes'] if i%2==0 else list(reversed(protocol['modes']))):
   assert all(sha(out/n)==h for n,h in frozen.items())
   source=out/'inputs'/c['source'];dest=out/mode/c['id']
   cmd=[sys.executable,'-m','agora.routed_cli','--source',str(source),'--source-id',c['id'],'--sha256',sha(source),'--question',c['question'],'--parts',str(out/'inputs'/c['parts']),'--response-language',c['language'],'--answer-profile','concise-v1','--response-format',mode,'--model','glm-5.3-flash','--out',str(dest)]
   start=time.monotonic()
   try:p=subprocess.run(cmd,env=env,timeout=110);code=p.returncode
   except subprocess.TimeoutExpired:code=None
   file=dest/'result.json';r=json.loads(file.read_text()) if file.exists() else {}
   row={'case':c['id'],'mode':mode,'seconds':round(time.monotonic()-start,3),'exit_code':code,'status':r.get('execution_status','unknown'),'diagnostic':r.get('diagnostic'),'result_sha256':sha(file) if file.exists() else None,'tokens':r.get('response',{}).get('usage',{}).get('total_tokens')};rows.append(row)
   (out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
   if not r or r.get('execution_status')=='failed':return 2
 assert all(sha(out/n)==h for n,h in frozen.items())
 return 0
if __name__=='__main__':raise SystemExit(main())
