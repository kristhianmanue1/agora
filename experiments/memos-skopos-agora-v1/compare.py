import sys,json,time,uuid,hashlib,urllib.request
from pathlib import Path
sys.path[:0]=['/Users/krisnova/www/aria/agora/src','/Users/krisnova/www/aria/skopos/src']
from skopos.captura import extraer_turnos
from agora.source import FileSourceAdapter,digest,SourceError
from agora.passages import prepare
out=Path(sys.argv[1]);out.mkdir(exist_ok=False,parents=True)
cases=[{'id':'conflict','text':'Synthetic project Juniper. Alice states that the delivery is approved for Tuesday.\n\nBob states that the same delivery is approved for Wednesday. Neither statement supersedes the other. The coordinator has not resolved this conflict.\n\nNo budget amount or budget owner is provided.','question':'What is the approved delivery day, budget amount and budget owner for project Juniper?','expected':'Preserve Tuesday versus Wednesday as unresolved; amount and owner unknown.'},{'id':'correction','text':'Synthetic project Maple. Earlier record: delivery was approved for Tuesday.\n\nExplicit correction from the coordinator: Wednesday replaces Tuesday as the approved delivery day. No calendar date, month or year is provided.\n\nPriya is the delivery owner. Budget approval remains pending.','question':'What is the currently approved delivery day and exact calendar date, who owns delivery, and is the budget approved for project Maple?','expected':'Wednesday replaces Tuesday; no calendar date; Priya owns delivery; budget pending.'}]
(out/'cases.json').write_text(json.dumps(cases,indent=2))
def call(name,path,body):
 f=out/(name+'.json');r={'path':path,'request':body,'status':'attempted'};f.write_text(json.dumps(r));t=time.monotonic()
 try:
  req=urllib.request.Request('http://127.0.0.1:9696'+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=180) as response:r.update(http=response.status,response=json.load(response),status='returned')
 except Exception as e:r.update(error_type=type(e).__name__,status='uncertain_or_failed');raise
 finally:r['seconds']=time.monotonic()-t;f.write_text(json.dumps(r,indent=2))
 print(name,r['status'],flush=True)
 if r['response'].get('code',200)!=200:raise RuntimeError('Application error; no retry')
 return r['response']
for c in cases:
 p=out/(c['id']+'.txt');p.write_text(c['text']);rev=digest(p.read_bytes());roll=out/(c['id']+'.jsonl')
 events=[{'type':'response_item','payload':{'type':'message','role':'user','content':[{'type':'input_text','text':c['text']}]}},{'type':'event_msg','timestamp':'2026-10-02T00:00:00Z','payload':{'type':'task_complete','turn_id':c['id']}}]
 roll.write_text(''.join(json.dumps(e)+'\n' for e in events));t=time.monotonic();turns=extraer_turnos(roll);elapsed=time.monotonic()-t
 assert len(turns)==1;turn=turns[0];raw=roll.read_bytes()[turn.offset_inicio:turn.offset_fin]
 sk={'exact_content':turn.texto_usuario==c['text'],'fragment_hash_matches':hashlib.sha256(raw).hexdigest()==turn.fragmento_sha256,'seconds':elapsed,'turn_id':turn.turn_id,'offset_start':turn.offset_inicio,'offset_end':turn.offset_fin};assert sk['exact_content'] and sk['fragment_hash_matches']
 adapter=FileSourceAdapter(p,c['id']);t=time.monotonic();env,retrieval,_=prepare(adapter,rev,c['question'],'retrieve',content_budget=2048,top_k=3);elapsed=time.monotonic()-t
 assert env is not None
 exact=all(c['text'].encode()[s['start_byte']:s['end_byte']]==s['text'].encode() for s in env['spans']);assert exact
 p.write_text(c['text']+'\nChanged after pinning.')
 try:adapter.fetch(rev,[(0,10)]);rejected=False
 except SourceError as e:rejected=str(e)=='source_revision_mismatch'
 p.write_text(c['text']);assert rejected
 (out/(c['id']+'-local.json')).write_text(json.dumps({'skopos':sk,'agora':{'envelope':env,'retrieval':retrieval,'exact_spans':exact,'changed_source_rejected':rejected,'seconds':elapsed},'source_sha256':rev},indent=2))
 cube='agora-three-'+c['id']+'-'+uuid.uuid4().hex[:10]
 call(c['id']+'-create','/product/create_cube',{'cube_name':cube,'cube_id':cube,'owner_id':'root'})
 call(c['id']+'-add','/product/add',{'user_id':'root','writable_cube_ids':[cube],'session_id':cube,'messages':[{'role':'user','content':c['text']}],'chat_history':[],'async_mode':'sync','info':{'fixture':True,'source_sha256':rev}})
 call(c['id']+'-all','/product/get_all',{'user_id':'root','mem_cube_ids':[cube],'memory_type':'text_mem'})
 call(c['id']+'-search','/product/search',{'query':c['question'],'user_id':'root','readable_cube_ids':[cube],'session_id':cube,'relativity':0.1,'top_k':10,'include_preference':False,'search_tool_memory':False,'search_skill_memory':False,'chat_history':[],'internet_search':False})
 call(c['id']+'-chat','/product/chat/complete',{'query':c['question'],'user_id':'root','readable_cube_ids':[cube],'writable_cube_ids':[],'session_id':cube,'relativity':0.1,'history':[],'include_preference':False,'internet_search':False,'add_message_on_answer':False,'model_name_or_path':'glm-5.3-flash','max_tokens':1024,'temperature':0,'system_prompt':'Answer only from supplied evidence. Preserve unresolved contradictions. Do not invent dates, amounts, owners or approvals. Explicitly state missing information.'})
print('DONE',out,flush=True)
