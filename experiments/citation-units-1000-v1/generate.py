import json,hashlib,sys,time
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter
from agora.plan_generation import live_provider
f=json.loads((B/'freeze.json').read_text());source=B.parent/'rubric-candidates-v1/inputs/source.txt';assert hashlib.sha256(source.read_bytes()).hexdigest()==f['source_sha256'];out=B/'runs-generation';out.mkdir(mode=0o700,exist_ok=False)
def dump(name,v):(out/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
attempts=0
def provider(system,user):
 global attempts
 assert attempts==0;attempts+=1;dump('request.json',dict(system=system,user=user));dump('receipt.json',dict(status='attempted',http_attempts=1));start=time.monotonic()
 try:
  result=live_provider(system,user,max_tokens=4096,json_object=True);dump('response.json',result);dump('receipt.json',dict(status='returned',http_attempts=1,elapsed_seconds=round(time.monotonic()-start,3)));return result
 except Exception as exc:
  dump('receipt.json',dict(status='failed',error=type(exc).__name__,http_attempts=1,elapsed_seconds=round(time.monotonic()-start,3)));raise
candidate=query_evidence(FileSourceAdapter(source,'qasper:1911.10401'),f['source_sha256'],f['question'],[dict(id='P1',question=f['question'])],provider,content_budget=60000,prompt_budget=100000,citation_mode='ids',response_language='en',max_unit_bytes=1000);dump('candidate.json',candidate)
print(json.dumps(dict(execution_status=candidate['execution_status'],http_attempts=attempts,diagnostics=candidate.get('diagnostics'),parts=candidate.get('parts')),ensure_ascii=False))
