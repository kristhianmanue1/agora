import json,hashlib,importlib.util
from pathlib import Path
r=Path(__file__).resolve().parents[2]
for name in ['sufficiency-axes-v1','sufficiency-long-reserved-v1']:
 b=r/'experiments'/name;f=json.loads((b/'freeze.json').read_text());cases=json.loads((b/'inputs/cases.json').read_text());gold={c['id']:c for c in json.loads((b/'gold.json').read_text())}
 for file,key in [('inputs/cases.json','cases_sha256'),('gold.json','gold_sha256')]:assert hashlib.sha256((b/file).read_bytes()).hexdigest()==f[key]
 spec=importlib.util.spec_from_file_location('runner',b/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 providers={}
 for provider in ['jev','glm']:
  rows=[]
  for c in cases:
   p=b/f'runs-{provider}'/(c['id']+'.json')
   if not p.exists():raise RuntimeError('incomplete run '+str(p))
   x=json.loads(p.read_text())
   if x['status']!='completed':raise RuntimeError('not completed '+str(p))
   body=x['request'];state=body['state'] if provider=='jev' else body['messages'][1]['content'];assert json.loads(state)=={k:c[k] for k in ('task','evidence','summary')}
   a=m.choices(provider,x['response']);raw=x['response'];usage=raw.get('usage',{})
   rows.append(dict(id=c['id'],status=x['status'],observed=a,expected={k:gold[c['id']][k] for k in a},matches={k:a[k]==gold[c['id']][k] for k in a},context=gold[c['id']].get('context','diagnostic'),mode=gold[c['id']].get('mode'),request_sha256=x['request_sha256'],response_sha256=hashlib.sha256(json.dumps(raw,sort_keys=True).encode()).hexdigest(),model_reported=raw.get('model'),elapsed_seconds=x['elapsed_seconds'],input_tokens=usage.get('input_tokens',usage.get('prompt_tokens')),output_tokens=usage.get('output_tokens',usage.get('completion_tokens'))))
  groups={}
  for context in sorted({x['context'] for x in rows}):
   selected=[x for x in rows if x['context']==context];groups[context]=dict(calls=len(selected),source_matches=sum(x['matches']['source_sufficiency'] for x in selected),summary_matches=sum(x['matches']['summary_coverage'] for x in selected),input_tokens=sum(x['input_tokens'] for x in selected),output_tokens=sum(x['output_tokens'] for x in selected),elapsed_seconds=round(sum(x['elapsed_seconds'] for x in selected),3))
  providers[provider]=dict(groups=groups,records=rows)
 result=dict(freeze_verified=True,gold_not_sent=True,providers=providers,monetary_cost='not verified: no billed ledger or frozen applicable price',retries=0)
 (b/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(name,json.dumps({p:v['groups'] for p,v in providers.items()}))
