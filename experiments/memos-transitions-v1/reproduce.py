import json,uuid,time,urllib.request,pathlib,sys
out=pathlib.Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
(out/'location').write_text(str(out))
cube='agora-transition-'+uuid.uuid4().hex[:12]
print(str(out),cube,flush=True)
def call(name,path,body=None):
 p=out/(name+'.json');p.write_text(json.dumps({'status':'attempted','path':path,'request':body}))
 t=time.monotonic();req=urllib.request.Request('http://127.0.0.1:9696'+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=180) as r: status=r.status; data=json.load(r)
 except Exception as e:
  p.write_text(json.dumps({'error':str(e),'path':path,'request':body}));raise
 p.write_text(json.dumps({'http':status,'seconds':time.monotonic()-t,'path':path,'request':body,'response':data},indent=2))
 print(name,status,flush=True);return data
def nodes(x):
 if isinstance(x,dict):
  if isinstance(x.get('memory'),str):yield x
  else:
   for k,v in x.items():
    if k!='metadata':yield from nodes(v)
 elif isinstance(x,list):
  for v in x:yield from nodes(v)
api=call('00-openapi','/openapi.json')
call('01-create','/product/create_cube',{'cube_name':cube,'owner_id':'root','cube_id':cube})
source='Synthetic project Cedar: the approved review meeting is on Tuesday. No calendar date has been specified.'
call('02-add','/product/add',{'user_id':'root','writable_cube_ids':[cube],'session_id':cube,'messages':[{'role':'user','content':source}],'chat_history':[],'async_mode':'sync','info':{'fixture':True}})
before=call('03-before','/product/get_all',{'user_id':'root','mem_cube_ids':[cube],'memory_type':'text_mem'})
ids=[n['id'] for n in nodes(before) if n.get('id')]
if not ids:raise RuntimeError('No memories ingested; stop without retry')
call('04-feedback','/product/feedback',{'user_id':'root','writable_cube_ids':[cube],'session_id':cube,'history':[{'role':'user','content':source},{'role':'assistant','content':'The approved Cedar review meeting is on Tuesday.'}],'retrieved_memory_ids':ids,'feedback_content':'Correction authorized for synthetic project Cedar: the approved review meeting is now Wednesday, replacing Tuesday. No calendar date is supplied. Preserve the old statement as historical only.','async_mode':'sync','corrected_answer':False,'info':{'fixture':True}})
call('05-after','/product/get_all',{'user_id':'root','mem_cube_ids':[cube],'memory_type':'text_mem'})
call('06-search','/product/search',{'user_id':'root','readable_cube_ids':[cube],'session_id':cube,'query':'What is the currently approved day for the Cedar review meeting?','relativity':0.1,'top_k':10,'include_preference':False,'search_tool_memory':False,'search_skill_memory':False,'chat_history':[],'internet_search':False})
print('DONE',out,flush=True)
