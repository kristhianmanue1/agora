"""Ten calls maximum; no retries/repairs. Frozen paired experiment and controls."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time,urllib.request

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def worker(source,dest):
 from agora.evidence_review import review_evidence
 from agora.__main__ import ENDPOINT
 attempts=0
 def provider(system,user):
  nonlocal attempts
  if attempts:raise RuntimeError('request_budget_exceeded')
  key=os.environ['ZAI_API_KEY']
  payload={'model':'glm-5.3-flash','messages':[{'role':'system','content':system},{'role':'user','content':user}],'max_tokens':8192,'temperature':0}
  req=urllib.request.Request(ENDPOINT,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
  class NoRedirect(urllib.request.HTTPRedirectHandler):
   def redirect_request(self,*a,**k):return None
  attempts+=1
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=180) as response:raw=response.read(1048577)
  if len(raw)>1048576:raise RuntimeError('response_too_large')
  data=json.loads(raw);choice=data['choices'][0]
  receipt={'content':choice['message']['content'],'finish_reason':choice.get('finish_reason'),'reported_model':data.get('model'),'response_id':data.get('id'),'usage':data.get('usage')}
  if key in json.dumps(receipt):raise RuntimeError('sensitive_response_rejected')
  return receipt
 r=review_evidence(json.loads(Path(source).read_text()),provider,response_language='es')
 r['http_attempts']=attempts;Path(dest).write_text(json.dumps(r,indent=2)+'\n')
 return 2 if r['execution_status']=='failed' else 0

def main():
 b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'runs/glm-01';out.mkdir(parents=True,exist_ok=False)
 shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(b/'inputs',out/'inputs');shutil.copyfile(__file__,out/'run.py')
 protocol={'max_calls':10,'model':'glm-5.3-flash','max_output_tokens':8192,'temperature':0,'socket_seconds':180,'process_seconds':200,'retries':0,'generation':'same question, full source, Spanish, IDs; only unit-byte limit differs (4096 vs1024), alternated order','review':'separate calls same model; citations only; no gold; no independence claim','controls':'English artifact; positive supported claim and wrong-subject/negation claims','stop':'transport/access/integrity failure; preserve structural rejects','metrics':'acceptance, quoted bytes, generation+review tokens/time, language/support/relevance flags; known gold reviewed separately; no official QASPER score'}
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2));frozen={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'freeze.json').write_text(json.dumps(frozen,indent=2))
 rows=[];env=dict(os.environ,PYTHONPATH=str(out/'code'),PYTHONDONTWRITEBYTECODE='1')
 def call(name,kind,cmd,path):
  assert all(sha(out/n)==h for n,h in frozen.items())
  start=time.monotonic()
  try:p=subprocess.run(cmd,env=env,timeout=200);code=p.returncode
  except subprocess.TimeoutExpired:code=None
  r=json.loads(path.read_text()) if path.exists() else {}
  row={'case':name,'kind':kind,'seconds':round(time.monotonic()-start,3),'exit_code':code,'status':r.get('execution_status','unknown'),'diagnostics':r.get('diagnostics'),'tokens':r.get('response',{}).get('usage',{}).get('total_tokens'),'path':str(path.relative_to(out)),'sha256':sha(path) if path.exists() else None};rows.append(row)
  (out/'execution.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
  if not r or r.get('execution_status')=='failed':raise RuntimeError('transport_or_execution_failure')
  return r
 def review(name,source):
  dest=out/(name+'-review.json');return call(name,'review',[sys.executable,str(out/'run.py'),'--worker',str(source),str(dest)],dest)
 for control in ('C-language','C-support'):review(control,out/'inputs'/(control+'.json'))
 for i,c in enumerate(json.loads((out/'inputs/cases.json').read_text())):
  for size in ([4096,1024] if i%2==0 else [1024,4096]):
   name=c['id']+'-'+str(size);source=out/'inputs'/c['source'];dest=out/name
   cmd=[sys.executable,'-m','agora.evidence_cli','--source',str(source),'--source-id',c['paper_id'],'--sha256',sha(source),'--question',c['question'],'--aspects',str(out/'inputs'/c['aspects']),'--citation-mode','ids','--response-language','es','--max-unit-bytes',str(size),'--content-budget','40000','--prompt-budget','200000','--model','glm-5.3-flash','--max-output-tokens','8192','--timeout-seconds','180','--out',str(dest)]
   result=call(name,'generation',cmd,dest/'result.json')
   if result['execution_status']=='complete':review(name,dest/'result.json')
 assert all(sha(out/n)==h for n,h in frozen.items())
 return 0
if __name__=='__main__':raise SystemExit(worker(sys.argv[2],sys.argv[3]) if len(sys.argv)>1 and sys.argv[1]=='--worker' else main())
