"""One predeclared operation, one provider request at most."""
import argparse
import json
import os
from pathlib import Path
import urllib.request
from agora.__main__ import ENDPOINT
from agora.source import FileSourceAdapter, SourceError, digest, encode_record
from agora.sufficiency import assess
from agora.passages import prepare, query_passages

class MeteredAdapter(FileSourceAdapter):
    read_bytes = 0
    read_operations = 0
    def _read(self, revision):
        data = super()._read(revision)
        self.read_bytes += len(data)
        self.read_operations += 1
        return data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    base = Path(__file__).resolve().parent
    case = next(c for c in json.loads((base/'cases.json').read_text()) if c['id']==args.case)
    args.out.mkdir(exist_ok=False)
    source = base/case['source']
    raw = source.read_bytes()
    revision = digest(raw)
    adapter = MeteredAdapter(source, case['source_id'])
    options = {'content_budget': 2048, 'top_k': 3}
    if case['mode']=='reference': options['ranges']=case['ranges']
    envelope, retrieval, _ = prepare(adapter, revision, case['question'], case['mode'], **options)
    attempts = 0
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
        if key in json.dumps(receipt):raise SourceError('sensitive_response_rejected')
        return receipt

    if envelope is None:
        result = {'execution_status':'not_evaluated','diagnostic':'no_passages'}
    elif case['operation']=='judge':
        data = encode_record(envelope)
        result = assess(adapter, revision, case['question'], data, digest(data), provider)
    else:
        # Fixed paired experiment: use exactly the same selected spans, irrespective of judge output.
        ranges = [(s['start_byte'],s['end_byte']) for s in envelope['spans']]
        result = query_passages(adapter, revision, case['question'], provider, mode='reference', ranges=ranges, content_budget=2048)
    result.update(http_attempts=attempts, experiment_mode=case['mode'], operation=case['operation'],
                  retrieval_observed=retrieval, source_bytes=len(raw),
                  local_source_bytes_read=len(raw)+adapter.read_bytes,
                  local_source_read_operations=1+adapter.read_operations,
                  selected_bytes=envelope['delivered_bytes'] if envelope else 0)
    (args.out/'result.json').write_text(json.dumps(result,ensure_ascii=True,indent=2)+'\n')
    return 0 if result['execution_status']=='complete' else 2

if __name__=='__main__': raise SystemExit(main())
