import os,sys,json,time
from pathlib import Path
sys.path.insert(0,'/Users/krisnova/www/aria/agora/src')
os.environ['ZAI_API_KEY']=os.environ['SKOPOS_LLM_API_KEY']
from agora.passage_cli import main
from agora.passages import query_passages
from agora.source import FileSourceAdapter
root=Path('/tmp/memos-long-reserved-v1');out=Path('/tmp/agora-scope-guard-v1');out.mkdir(exist_ok=False)
for c in json.load(open(root/'cases.json')):
 q=c['questions'][0 if c['id']=='1601.03313' else 1]
 old=json.load(open(root/'agora'/q['id']/'result.json'))
 replay=query_passages(FileSourceAdapter(root/c['source'],c['id']),c['sha256'],q['question'],lambda *_:old['response'],content_budget=12000,top_k=6,scope_guard=True)
 assert replay['answer_status']=='candidate_requires_expansion'
 (out/(q['id']+'-replay.json')).write_text(json.dumps(replay,indent=2))
 sys.argv=['agora','--source',str(root/c['source']),'--source-id',c['id'],'--sha256',c['sha256'],'--question',q['question'],'--mode','source','--scope-guard','--content-budget','100000','--prompt-budget','131072','--model','glm-5.3-flash','--max-output-tokens','4096','--timeout-seconds','180','--out',str(out/q['id'])]
 t=time.monotonic();code=main();(out/(q['id']+'-time.json')).write_text(json.dumps({'seconds':time.monotonic()-t,'exit_code':code}))
