import json,hashlib,importlib.util
from pathlib import Path
BASE=Path(__file__).resolve().parent
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
prior=module('prior',BASE.parent/'reviewer-separated-v1/run.py')
def payload(provider,c):
 if provider!='glm':raise ValueError('glm_only')
 assert c['axis']=='coverage';_,body=prior.payload('jev',c);q=body['questions']['coverage'];system=q['instructions']+' Criteria: '+json.dumps(q['criteria'])+' Return only a JSON object with one key "coverage" whose value is one of the criteria keys.'
 return 'https://api.z.ai/api/coding/paas/v4/chat/completions',dict(model='glm-5.3-flash',temperature=0,max_tokens=2048,response_format={'type':'json_object'},messages=[dict(role='system',content=system),dict(role='user',content=body['state'])])
def label(provider,raw):
 c=raw['choices'][0]
 if c.get('finish_reason')!='stop':raise ValueError('incomplete_response')
 obj=json.loads(c['message']['content'])
 if set(obj)!={'coverage'} or obj['coverage'] not in prior.CRITERIA['coverage']:raise ValueError('invalid_coverage')
 return obj['coverage']
if __name__=='__main__':
 f=json.loads((BASE/'freeze.json').read_text());assert hashlib.sha256((BASE/'inputs/cases.json').read_bytes()).hexdigest()==f['cases_sha256'];m=module('transport',BASE.parent/'reviewer-comparison-v1/run.py');m.BASE=BASE/'inputs';m.payload=payload;m.label=label;m.main()
