"""Bounded synthetic traversal: maximum nine requests, no retry."""
import json
import os
from pathlib import Path
import shutil
import time
import urllib.request
from agora.__main__ import ENDPOINT
from agora.source import FileSourceAdapter,digest
from agora.traversal import walk


def main():
    root=Path(__file__).resolve().parents[2]
    old=root/'experiments/sufficiency-large-v1/runs/glm-01'
    manifest=json.loads((old/'freeze.json').read_text())
    assert all(digest((old/k).read_bytes())==v for k,v in manifest.items())
    out=root/'experiments/traversal-v1/runs/glm-01';out.mkdir(parents=True,exist_ok=False)
    shutil.copytree(root/'src/agora',out/'code/agora',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(__file__,out/'run.py');shutil.copyfile(old/'source.txt',out/'source.txt')
    config={'question':'Resume todas las fases del programa Vela e identifica sus responsables.',
            'unit_bytes':16384,'max_calls':9,'total_prompt_budget':524288,
            'per_prompt_budget':65536,'retained_budget':16384,
            'requested_model':'glm-5.3-flash','max_output_tokens':2048,'socket_timeout':90,
            'expected_facts':['Aina','Berto','Cora','Darío'],'synthetic':True,
            'independent_holdout':False,'synthesis':False}
    (out/'config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
    manifest={str(p.relative_to(out)):digest(p.read_bytes()) for p in out.rglob('*') if p.is_file()}
    (out/'freeze.json').write_text(json.dumps(manifest,indent=2)+'\n')
    attempts=0
    def provider(system,user):
        nonlocal attempts
        if attempts>=9:raise RuntimeError('request_budget_exceeded')
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
        (out/f'receipt-{attempts:02d}.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'call':attempts,'usage':receipt.get('usage'),'finish_reason':receipt.get('finish_reason')}),flush=True)
        return receipt

    adapter=FileSourceAdapter(out/'source.txt','large-synthetic-v1')
    revision=digest((out/'source.txt').read_bytes());started=time.monotonic()
    result=walk(adapter,revision,config['question'],provider,unit_bytes=16384,max_calls=9,
                total_prompt_budget=524288,per_prompt_budget=65536,retained_budget=16384)
    result['elapsed_seconds']=round(time.monotonic()-started,3)
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    assert all(digest((out/k).read_bytes())==v for k,v in manifest.items())
    assert all(digest((root/'src'/Path(k).relative_to('code')).read_bytes())==v
               for k,v in manifest.items() if k.startswith('code/'))
    print(json.dumps({'status':result['execution_status'],'traversal':result['traversal_status'],
                      'calls':result['provider_calls'],'retained_bytes':result['retained_bytes'],
                      'seconds':result['elapsed_seconds']}),flush=True)

if __name__=='__main__':main()
