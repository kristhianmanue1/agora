"""Fixed real-document comparison. Criteria never enter provider prompts."""
import argparse,json,os,time
from pathlib import Path
import urllib.request
from agora.__main__ import ENDPOINT
from agora.source import FileSourceAdapter,digest
from agora.traversal import walk
from agora.passages import query_passages
from agora.traversal_query import query_traversal

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--stage',choices=['baseline','walk','answer'],required=True);args=p.parse_args()
    base=Path(__file__).resolve().parent
    case=next(c for c in json.loads((base/'cases.json').read_text()) if c['id']==args.case)
    dest=base/case['id']/args.stage;dest.mkdir(parents=True,exist_ok=False)
    source=base/'source.txt';revision=digest(source.read_bytes());adapter=FileSourceAdapter(source,'real-docx-extracted-v1')
    attempts=0;limit=4 if args.stage=='walk' else 1
    def provider(system,user):
        nonlocal attempts
        if attempts>=limit:raise RuntimeError('request_budget_exceeded')
        key=os.environ.get('ZAI_API_KEY')
        if not key:raise RuntimeError('provider_key_missing')
        payload={'model':'glm-5.3-flash','messages':[{'role':'system','content':system},{'role':'user','content':user}],
                 'temperature':0,'max_tokens':8192}
        request=urllib.request.Request(ENDPOINT,data=json.dumps(payload).encode(),
            headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*a,**k):return None
        attempts+=1
        with urllib.request.build_opener(NoRedirect()).open(request,timeout=90) as response:raw=response.read(1048577)
        if len(raw)>1048576:raise RuntimeError('provider_response_too_large')
        data=json.loads(raw);choice=data['choices'][0]
        receipt={'content':choice['message']['content'],'finish_reason':choice.get('finish_reason'),
                 'requested_model':'glm-5.3-flash','reported_model':data.get('model'),
                 'response_id':data.get('id'),'usage':data.get('usage')}
        if key in json.dumps(receipt):raise RuntimeError('sensitive_response_rejected')
        (dest/f'receipt-{attempts}.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'case':case['id'],'stage':args.stage,'call':attempts,'usage':receipt.get('usage')}),flush=True)
        return receipt

    start=time.monotonic()
    if args.stage=='walk':
        result=walk(adapter,revision,case['question'],provider,unit_bytes=4096,max_calls=4,
                    total_prompt_budget=65536,per_prompt_budget=32768,retained_budget=8192)
    elif args.stage=='baseline':
        result=query_passages(adapter,revision,case['question'],provider,mode='source',content_budget=32768,prompt_budget=32768)
    else:
        data=(base/case['id']/'walk/result.json').read_bytes()
        result=query_traversal(adapter,revision,case['question'],data,digest(data),provider,prompt_budget=32768)
    result['elapsed_seconds']=round(time.monotonic()-start,3);result['http_attempts']=attempts
    (dest/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'case':case['id'],'stage':args.stage,'status':result['execution_status'],'diagnostic':result.get('diagnostic'),'calls':attempts}),flush=True)
    return 0 if result['execution_status']=='complete' else 2

if __name__=='__main__':raise SystemExit(main())
