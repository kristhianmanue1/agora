import json,hashlib,importlib.util
from pathlib import Path
BASE=Path(__file__).resolve().parent
path=BASE.parent/'reviewer-comparison-v1/run.py';s=importlib.util.spec_from_file_location('transport',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def payload(provider,c):
 if provider!='glm':raise ValueError('generator_must_be_glm')
 return 'https://api.z.ai/api/coding/paas/v4/chat/completions',dict(model='glm-5.3-flash',temperature=0,max_tokens=2048,response_format={'type':'json_object'},messages=[dict(role='system',content=c['system']),dict(role='user',content=c['user'])])
f=json.loads((BASE/'continuation-01.json').read_text());data=(BASE/'inputs/continuation-01/cases.json').read_bytes();assert hashlib.sha256(data).hexdigest()==f['cases_sha256'];assert len(json.loads(data))==16
assert all(hashlib.sha256((BASE/'runs-generation'/f'{cid}.json').read_bytes()).hexdigest()==h for cid,h in f['prior_journal_hashes'].items())
assert not set(f['pending_ids']) & set(f['prior_journal_hashes'])
m.BASE=BASE/'inputs/continuation-01';m.payload=payload;m.label=lambda provider,raw:'received';m.main()
