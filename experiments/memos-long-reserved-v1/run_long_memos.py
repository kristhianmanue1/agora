import json,time,urllib.request,uuid,hashlib
from pathlib import Path
root=Path('/tmp/memos-long-reserved-v1');out=root/'memos';out.mkdir(exist_ok=False)
def call(name,path,body):
 trace='long-'+uuid.uuid4().hex; p=out/(name+'.json');r={'trace':trace,'path':path,'status':'attempted','request':body};p.write_text(json.dumps(r));t=time.monotonic()
 try:
  req=urllib.request.Request('http://127.0.0.1:9697'+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-trace-id':trace})
  with urllib.request.urlopen(req,timeout=180) as res:r.update(http=res.status,response=json.load(res),status='returned')
 except Exception as e:r.update(error_type=type(e).__name__,status='uncertain_or_failed');raise
 finally:r['seconds']=time.monotonic()-t;p.write_text(json.dumps(r,indent=2))
 print(name,r['status'],round(r['seconds'],2),flush=True)
 if r['response'].get('code',200)!=200:raise RuntimeError('Application error')
for c in json.loads((root/'cases.json').read_text()):
 p=root/c['source'];assert hashlib.sha256(p.read_bytes()).hexdigest()==c['sha256'];cube='agora-long-'+c['id'].replace('.','-')+'-'+uuid.uuid4().hex[:8]
 call(c['id']+'-create','/product/create_cube',{'cube_name':cube,'cube_id':cube,'owner_id':'root'})
 call(c['id']+'-add','/product/add',{'user_id':'root','writable_cube_ids':[cube],'session_id':cube,'messages':[{'role':'user','content':p.read_text()}],'chat_history':[],'async_mode':'sync','info':{'source_sha256':c['sha256'],'fixture':True,'source_id':c['id']}})
 call(c['id']+'-all','/product/get_all',{'user_id':'root','mem_cube_ids':[cube],'memory_type':'text_mem'})
 for q in c['questions']:
  call(q['id']+'-search','/product/search',{'query':q['question'],'user_id':'root','readable_cube_ids':[cube],'session_id':cube,'relativity':0.1,'top_k':10,'include_preference':False,'search_tool_memory':False,'search_skill_memory':False,'chat_history':[],'internet_search':False})
  call(q['id']+'-chat','/product/chat/complete',{'query':q['question'],'user_id':'root','readable_cube_ids':[cube],'writable_cube_ids':[],'session_id':cube,'relativity':0.1,'history':[],'include_preference':False,'internet_search':False,'add_message_on_answer':False,'model_name_or_path':'glm-5.3-flash','max_tokens':2048,'temperature':0,'system_prompt':'Answer in English only from supplied evidence. Cite supporting evidence. Preserve uncertainty and explicitly state when information is missing. Do not invent facts.'})
