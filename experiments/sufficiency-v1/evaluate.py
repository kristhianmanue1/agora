"""Single synthetic case worker, at most one HTTP request."""
import argparse
import json
import os
from pathlib import Path
import urllib.request
from agora.__main__ import ENDPOINT
from agora.source import FileSourceAdapter, digest, encode_record
from agora.sufficiency import assess


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();base=Path(__file__).resolve().parent
    case=next(c for c in json.loads((base/'cases.json').read_text()) if c['id']==args.case)
    args.out.mkdir(exist_ok=False)
    source=base/case['source'];revision=digest(source.read_bytes())
    adapter=FileSourceAdapter(source,case['source_id'])
    envelope=encode_record(adapter.fetch(revision,case['ranges']))
    attempts=0
    def provider(system,user):
        nonlocal attempts
        if attempts:raise RuntimeError('request_budget_exceeded')
        key=os.environ.get('ZAI_API_KEY')
        if not key:raise RuntimeError('provider_key_missing')
        payload={'model':'glm-5.3-flash','messages':[{'role':'system','content':system},{'role':'user','content':user}],
                 'temperature':0,'max_tokens':2048}
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
        return receipt
    result=assess(adapter,revision,case['question'],envelope,digest(envelope),provider)
    result['http_attempts']=attempts
    (args.out/'envelope.json').write_bytes(envelope)
    (args.out/'result.json').write_text(json.dumps(result,ensure_ascii=True,indent=2)+'\n')
    return 0 if result['execution_status']=='complete' else 2


if __name__=='__main__':raise SystemExit(main())
