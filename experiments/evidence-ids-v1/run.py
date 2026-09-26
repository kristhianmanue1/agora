"""Eight calls at most; modes paired, order alternated, no repairs/retries."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/glm-01';out.mkdir(parents=True,exist_ok=False)
 shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
 shutil.copytree(b/'inputs',out/'inputs');shutil.copyfile(__file__,out/'run.py')
 protocol={'max_calls':8,'model':'glm-5.3-flash','temperature':0,'max_tokens':8192,'socket_seconds':180,'process_seconds':200,'retries':0,'stop':'transport/access/integrity failure; record and continue rejections','modes':['literal','ids'],'order':'alternate by case; G1 literal first','budgets':{'content_bytes':40000,'prompt_bytes':200000,'quote_occurrences_per_part':12,'quote_bytes_per_part':12000,'quote_bytes_total':48000},'claim':'test valid references and delivery; not automatic entailment or retrieval savings','cost':'includes failures and expanded evidence size; preparation/review excluded from process time'}
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 frozen={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'freeze.json').write_text(json.dumps(frozen,indent=2)+'\n')
 rows=[];env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1')
 for i,c in enumerate(json.loads((out/'inputs/cases.json').read_text())):
  for mode in (['literal','ids'] if i%2==0 else ['ids','literal']):
   assert all(sha(out/n)==h for n,h in frozen.items())
   source=out/'inputs'/c['source'];dest=out/mode/c['id']
   cmd=[sys.executable,'-m','agora.evidence_cli','--source',str(source),'--source-id',c.get('paper_id',c['id']),'--sha256',sha(source),'--question',c['question'],'--aspects',str(out/'inputs'/c['aspects']),'--citation-mode',mode,'--content-budget','40000','--prompt-budget','200000','--model','glm-5.3-flash','--max-output-tokens','8192','--timeout-seconds','180','--out',str(dest)]
   if c.get('selection'):
    for s,e in json.loads((out/'inputs'/c['selection']).read_text())['ranges']:cmd+=['--range',f'{s}:{e}']
   start=time.monotonic()
   try:p=subprocess.run(cmd,env=env,timeout=200);code=p.returncode
   except subprocess.TimeoutExpired:code=None
   f=dest/'result.json';r=json.loads(f.read_text()) if f.exists() else {}
   row={'case':c['id'],'mode':mode,'seconds':round(time.monotonic()-start,3),'exit_code':code,'status':r.get('execution_status','unknown'),'diagnostics':r.get('diagnostics',r.get('diagnostic')),'tokens':r.get('response',{}).get('usage',{}).get('total_tokens'),'sha256':sha(f) if f.exists() else None};rows.append(row)
   (out/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
   if not r or r.get('execution_status')=='failed':return 2
 assert all(sha(out/n)==h for n,h in frozen.items());return 0
if __name__=='__main__':raise SystemExit(main())
