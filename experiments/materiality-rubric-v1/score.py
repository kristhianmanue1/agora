import json,hashlib,importlib.util
from pathlib import Path
B=Path(__file__).resolve().parent;load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=load(B/'freeze.json')
for name,key in [('inputs/cases.json','cases_sha256'),('key.json','key_sha256'),('rubric.json','rubric_sha256')]:assert sha(B/name)==f[key]
s=importlib.util.spec_from_file_location('review',B/'run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);cases={c['id']:c for c in load(B/'inputs/cases.json')};rows=[]
for k in load(B/'key.json'):
 p=B/'runs-review'/f"{k['id']}.json";r=load(p) if p.exists() else dict(status='not_run');u=r.get('response',{}).get('usage',{})
 if p.exists():assert r['request']==m.payload('glm',cases[k['id']])[1]
 observed=r.get('label');valid=r['status']=='completed' and type(observed) is dict and set(observed)==set(k['expected']);rows.append(dict(k,status=r['status'],valid=valid,observed=observed,exact_match=valid and observed==k['expected'],false_covered=[i for i,v in k['expected'].items() if v!='covered' and valid and observed[i]=='covered'],input_tokens=u.get('prompt_tokens'),output_tokens=u.get('completion_tokens'),elapsed_seconds=r.get('elapsed_seconds',0),model=r.get('response',{}).get('model')))
summary=dict(planned=len(rows),completed=sum(x['status']=='completed' for x in rows),valid=sum(x['valid'] for x in rows),exact_matches=sum(x['exact_match'] for x in rows),false_covered=sum(len(x['false_covered']) for x in rows),input_tokens=sum(x['input_tokens'] or 0 for x in rows),output_tokens=sum(x['output_tokens'] or 0 for x in rows),elapsed_seconds=round(sum(x['elapsed_seconds'] for x in rows),3));(B/'result.json').write_text(json.dumps(dict(summary=summary,records=rows,limits=f['limits']),ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary));print([(x['group'],x['observed'],x['exact_match']) for x in rows])
