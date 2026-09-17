"""CLI de una transformación: proveedor GLM explícito, una solicitud, sin retry."""
import argparse
import json
import os
from pathlib import Path
import urllib.request
from .transform import TransformError, transform

ENDPOINT='https://api.z.ai/api/coding/paas/v4/chat/completions'

def token_limit(value):
    try:
        number=int(value)
    except ValueError:
        raise argparse.ArgumentTypeError('token limit must be an integer') from None
    if not 128<=number<=8192:
        raise argparse.ArgumentTypeError('token limit must be between 128 and 8192')
    return number

def timeout_limit(value):
    try:
        number=int(value)
    except ValueError:
        raise argparse.ArgumentTypeError('timeout must be an integer') from None
    if not 1<=number<=180:
        raise argparse.ArgumentTypeError('timeout must be between 1 and 180 seconds')
    return number

def main():
    parser=argparse.ArgumentParser(description='Resumen candidato con referencias; requiere revisión semántica.')
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--sha256',required=True)
    parser.add_argument('--source-id',required=True)
    parser.add_argument('--required-line',type=int,action='append',default=[])
    parser.add_argument('--model',required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--summary-max-bytes',type=int,default=None)
    parser.add_argument('--max-output-tokens',type=token_limit,default=1200)
    parser.add_argument('--timeout-seconds',type=timeout_limit,default=45)
    args=parser.parse_args()
    # A new directory prevents overwriting a previous run, even if it failed.
    args.out.mkdir(parents=True,exist_ok=False)
    attempts=0
    def provider(system,user):
        nonlocal attempts
        if attempts: raise RuntimeError('request_budget_exceeded')
        key=os.environ.get('ZAI_API_KEY')
        if not key: raise RuntimeError('provider_key_missing')
        payload={'model':args.model,'messages':[{'role':'system','content':system},{'role':'user','content':user}],
                 'max_tokens':args.max_output_tokens,'temperature':0}
        attempts+=1
        request=urllib.request.Request(ENDPOINT,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
        # Refuse redirects so the authorization header cannot be forwarded elsewhere.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*a,**k): return None
        with urllib.request.build_opener(NoRedirect()).open(request,timeout=args.timeout_seconds) as response:
            raw=response.read(1_048_577)
        if len(raw)>1_048_576: raise RuntimeError('provider_response_too_large')
        data=json.loads(raw)
        content=data['choices'][0]['message']['content']
        # No chain-of-thought or arbitrary provider bodies are persisted.
        if key in json.dumps({'content':content,'usage':data.get('usage')}):
            raise RuntimeError('sensitive_response_rejected')
        return {'content':content,'requested_model':args.model,'reported_model':data.get('model'),
                'finish_reason':data['choices'][0].get('finish_reason'),'response_id':data.get('id'),'usage':data.get('usage'),'max_tokens':args.max_output_tokens}
    try:
        with args.source.open('rb') as stream:
            data=stream.read(4097)
        result=transform(data,args.sha256,args.source_id,args.required_line,provider,summary_limit=args.summary_max_bytes)
        result['http_attempts']=attempts
        result['implementation_hashes']={name:__import__('hashlib').sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ('transform.py','__main__.py')}
        code=0 if result['structural_status']=='valid' else 2
    except TransformError as exc:
        result={'execution_status':'rejected','diagnostic':str(exc),'http_attempts':attempts};code=2
    except Exception as exc:
        result={'execution_status':'failed','diagnostic':type(exc).__name__,'http_attempts':attempts};code=1
    result['request_config']={'requested_model':args.model,'max_output_tokens':args.max_output_tokens,'timeout_seconds':args.timeout_seconds,'summary_max_bytes':args.summary_max_bytes,'temperature':0}
    if result.get('structural_status')=='valid' and 'views' in result:
        (args.out/'summary.txt').write_text(result['views']['summary'],encoding='utf-8')
        (args.out/'source.txt').write_bytes(data)
        (args.out/'reading.txt').write_bytes(result['views']['reading'].encode('utf-8'))
        (args.out/'evidence.json').write_text(json.dumps(result['views']['evidence'],ensure_ascii=False,indent=2)+'\n')
    (args.out/'result.json').write_text(json.dumps(result,ensure_ascii=True,indent=2)+'\n')
    print(json.dumps({'exit_code':code,'execution_status':result['execution_status'],
        'structural_status':result.get('structural_status'),'review_status':result.get('review_status'),'http_attempts':attempts,
        'compression_status':result.get('compression',{}).get('status'),
        'reading_kind':result.get('reading_selection',{}).get('kind')}))
    return code

if __name__=='__main__': raise SystemExit(main())
