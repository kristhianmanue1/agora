import sys,json,subprocess,os
from pathlib import Path
sys.path.insert(0,'/Users/krisnova/www/aria/agora/src')
from agora.source import FileSourceAdapter,digest
from agora.subquestions import prepare_subquestions
from agora.evidence_ids import build_units
r=Path('/tmp/agora-plan-scope-cli-v1');r.mkdir(exist_ok=False);p=r/'source.txt';raw=b'Approve standards.\n\n'+b'Other information. '*100;p.write_bytes(raw)
plan=prepare_subquestions(FileSourceAdapter(p,'fixture'),digest(raw),dict(schema='agora/subquestions-input/v1-experimental',questions=[dict(id='a',query='Approve',reference_ranges=[])]),100,1)
pf=r/'plan.json';pf.write_text(json.dumps(plan));entry='/Users/krisnova/www/aria/agora/scripts/agora_issues.py';base=[sys.executable,entry,'--workspace',str(r/'workspace')]
subprocess.run(base+['init'],check=True,capture_output=True)
results=[]
for mode in ['literal','ids']:
 if mode=='literal':part=dict(id='P1',status='answer',answer='Approve standards.',quotes=['Approve standards.'])
 else:part=dict(id='P1',status='answered',claims=[dict(text='Approve standards.',evidence_ids=[build_units(plan['envelope'],'fixture',digest(raw))[0]['id']])],missing=[])
 response=r/(mode+'-response.json');response.write_text(json.dumps(dict(finish_reason='stop',content=json.dumps({'parts':[part]}))))
 args=base+['generate-plan','--source',str(p),'--plan',str(pf),'--expected-plan-sha256',digest(pf.read_bytes()),'--question','What is approved?','--response',str(response),'--citation-mode',mode,'--scope-guard','--out',str(r/mode)]
 c=subprocess.run(args,capture_output=True,text=True);assert c.returncode==0,c.stderr
 x=json.loads(c.stdout);assert x['requires_expansion'] and x['http_attempts']==0 and x['reading_budget_bytes']==100 and x['answer_status']=='candidate_requires_expansion'
 results.append(dict(mode=mode,command=args,output=x))
(r/'result.json').write_text(json.dumps(results,indent=2));print('Both CLI modes: scope guard, budget and zero HTTP verified')
