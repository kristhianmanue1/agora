"""Bounded local MemOS comparison; no retries or reuse of an existing run."""
import json,hashlib,time,urllib.request,urllib.error
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];f=json.loads((B/'freeze.json').read_text());out=B/'runs';out.mkdir(mode=0o700)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(Path(__file__))==f['runner_sha256']
def call(name,endpoint,body):
 p=out/(name+'.json');record=dict(endpoint=endpoint,request=body,status='attempted');p.write_text(json.dumps(record,ensure_ascii=False,indent=2));start=time.monotonic()
 try:
  req=urllib.request.Request('http://127.0.0.1:9696'+endpoint,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=180) as response:
   raw=response.read(8*1024*1024+1);assert len(raw)<=8*1024*1024;record.update(http_status=response.status,response=json.loads(raw),status='returned')
 except Exception as exc:
  record.update(status='uncertain_or_failed',error_type=type(exc).__name__)
 finally:
  record['seconds']=round(time.monotonic()-start,3);p.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 print(name,record['status'],record['seconds'],flush=True)
 if record['status']!='returned':raise SystemExit('Stop: inspect retained attempt; no retry')
 if isinstance(record['response'],dict) and record['response'].get('code',200) not in (0,200):raise SystemExit('Application response requires inspection; no retry')
 return record
for c in f['cases']:
 source=R/c['source'];assert sha(source)==c['source_sha256'];cube=c['cube_id'];session=cube+'-session'
 call(c['id']+'-create','/product/create_cube',dict(cube_name=cube,owner_id='root',cube_id=cube))
 call(c['id']+'-add','/product/add',dict(user_id='root',writable_cube_ids=[cube],session_id=session,messages=[dict(role='user',content=source.read_text())],chat_history=[],async_mode='sync',info=dict(source_id=c['id'],source_sha256=c['source_sha256'],source_type='comparison_fixture')))
 call(c['id']+'-before','/product/get_all',dict(user_id='root',mem_cube_ids=[cube],memory_type='text_mem'))
 for threshold in f['relativity_values']:
  call(c['id']+'-search-'+str(threshold),'/product/search',dict(query=c['question'],user_id='root',readable_cube_ids=[cube],session_id=session,relativity=threshold,top_k=10,include_preference=False,search_tool_memory=False,search_skill_memory=False,chat_history=[],internet_search=False))
 call(c['id']+'-chat','/product/chat/complete',dict(query=c['question'],user_id='root',readable_cube_ids=[cube],writable_cube_ids=[],session_id=session,relativity=f['chat_relativity'],history=[],include_preference=False,internet_search=False,add_message_on_answer=False,model_name_or_path='glm-5.3-flash',max_tokens=2048,temperature=0,system_prompt='Answer only from supplied retrieved evidence. State what is missing. Distinguish the latest observed correction from a guarantee about future changes. Include source references when available.'))
 call(c['id']+'-after','/product/get_all',dict(user_id='root',mem_cube_ids=[cube],memory_type='text_mem'))
