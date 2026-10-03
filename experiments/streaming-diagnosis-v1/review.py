import os,json,time,hashlib,urllib.request
from pathlib import Path
p=Path(__file__).parent;raw=(p/'request.json').read_bytes();f=json.loads((p/'freeze.json').read_text());assert hashlib.sha256(raw).hexdigest()==f['request_sha256'];out=p/'review.json'
with out.open('x') as h:json.dump({'status':'attempted','http_attempts':1},h)
t=time.monotonic();r={'http_attempts':1}
try:
 class NoRedirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,*a,**k):return None
 key=os.environ['TYPESAFE_API_KEY'];req=urllib.request.Request('https://api.typesafe.ai/v1/systemone',data=raw,headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=90) as response:body=response.read(1048577)
 assert len(body)<=1048576 and key.encode() not in body
 v=json.loads(body);qs=json.loads(raw)['questions'];assert set(v['answers'])==set(qs)
 for k,a in v['answers'].items():assert a['choice'] in qs[k]['criteria']
 r.update(status='complete',response=v)
except Exception as e:r.update(status='failed',error_type=type(e).__name__,http_code=getattr(e,'code',None))
r['seconds']=time.monotonic()-t;out.write_text(json.dumps(r,indent=2)+'\n')
