import sys,os,json,time,hashlib
from pathlib import Path
sys.path.insert(0,'/Users/krisnova/www/aria/agora/src')
os.environ['ZAI_API_KEY']=os.environ['SKOPOS_LLM_API_KEY']
from agora.passage_cli import main
root=Path('/tmp/memos-long-reserved-v3-ready');out=root/'agora';out.mkdir(exist_ok=False)
for c in json.loads((root/'cases.json').read_text()):
 p=root/c['source'];assert hashlib.sha256(p.read_bytes()).hexdigest()==c['sha256']
 for q in c['questions']:
  sys.argv=['agora','--source',str(p),'--source-id',c['id'],'--sha256',c['sha256'],'--question',q['question'],'--scope-guard','--mode','retrieve','--content-budget','12000','--top-k','6','--model','glm-5.3-flash','--max-output-tokens','4096','--timeout-seconds','180','--out',str(out/q['id'])]
  t=time.monotonic();code=main();(out/(q['id']+'-timing.json')).write_text(json.dumps({'seconds':time.monotonic()-t,'exit_code':code}))
