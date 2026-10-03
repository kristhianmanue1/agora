import sys,json,hashlib,time,os
os.environ["ZAI_API_KEY"]=os.environ["SKOPOS_LLM_API_KEY"]
from pathlib import Path
sys.path.insert(0,'/Users/krisnova/www/aria/agora/src')
from agora.passage_cli import main
root=Path(sys.argv[1])
for case in json.loads((root/'cases.json').read_text()):
 p=root/(case['id']+'.txt')
 if not p.exists():p.write_text(case['text'])
 assert p.read_text()==case['text']
 sys.argv=['agora.passage_cli','--source',str(p),'--source-id',case['id'],'--sha256',hashlib.sha256(p.read_bytes()).hexdigest(),'--question',case['question'],'--mode','retrieve','--content-budget','2048','--model','glm-5.3-flash','--max-output-tokens','2048','--timeout-seconds','180','--out',str(root/(case['id']+'-agora-live-v2'))]
 start=time.monotonic();code=main();(root/(case['id']+'-agora-timing-v2.json')).write_text(json.dumps({'seconds':time.monotonic()-start,'exit_code':code}))
 if code:break
