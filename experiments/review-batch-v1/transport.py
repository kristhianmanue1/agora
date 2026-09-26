"""Single GLM HTTP attempt; final content/usage only, no reasoning content."""
import json,os,sys,urllib.request
from pathlib import Path

def main():
 key=os.environ['ZAI_API_KEY'];payload=json.loads(Path(sys.argv[1]).read_text());timeout=float(sys.argv[2])
 req=urllib.request.Request('https://api.z.ai/api/coding/paas/v4/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
 class NoRedirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,*a,**k):return None
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=timeout) as response:raw=response.read(1048577)
 if len(raw)>1048576:raise RuntimeError('response_too_large')
 data=json.loads(raw);choice=data['choices'][0];r={'content':choice['message']['content'],'finish_reason':choice.get('finish_reason'),'reported_model':data.get('model'),'requested_model':payload['model'],'response_id':data.get('id'),'usage':data.get('usage')}
 if key in json.dumps(r):raise RuntimeError('sensitive_response_rejected')
 print(json.dumps(r))
if __name__=='__main__':
 try:main()
 except Exception as exc:print(json.dumps({'transport_error':type(exc).__name__}));raise SystemExit(2)
