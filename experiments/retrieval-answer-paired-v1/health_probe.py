import json,os,time,urllib.request,urllib.error
from pathlib import Path
b=Path(__file__).resolve().parent;p=b/'health-01.json';assert not p.exists()
record=dict(status='attempted',started_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),timeout_seconds=20,retries=0,model_requested='glm-5.3-flash');p.write_text(json.dumps(record,indent=2)+'\n');start=time.monotonic()
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**k):return None
body=dict(model='glm-5.3-flash',temperature=0,max_tokens=2048,response_format={'type':'json_object'},messages=[dict(role='user',content='Return only the JSON object {"ok":true}.')]);secret=os.environ['SKOPOS_LLM_API_KEY']
try:
 req=urllib.request.Request('https://api.z.ai/api/coding/paas/v4/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+secret})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=20) as res:data=res.read(1048577)
 if len(data)>1048576 or secret.encode() in data:raise ValueError('invalid_response')
 raw=json.loads(data);choice=raw['choices'][0];ok=choice.get('finish_reason')=='stop' and json.loads(choice['message']['content'])=={'ok':True};record.update(status='completed' if ok else 'invalid_output',model_reported=raw.get('model'),usage=raw.get('usage'),finish_reason=choice.get('finish_reason'))
except urllib.error.HTTPError as e:record.update(status='failed',error='HTTPError',http_status=e.code)
except Exception as e:record.update(status='failed',error=type(e).__name__)
record['elapsed_seconds']=round(time.monotonic()-start,3);p.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
