import json,sys,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path.insert(0,str(R/'src'))
from agora.issue_cli import main
f=json.loads((B/'controls-freeze.json').read_text());(B/'runs').mkdir();assert main(['--workspace',str(B/'inputs/workspace'),'init'])==0;results=[]
for c in f['cases']:
 args=['--workspace',str(B/'inputs/workspace'),'review-rubric-scoped','--part-id','P1','--question',c['question'],'--live','--out',str(B/'runs'/c['id'])]
 for key in ('source','candidate','rubric'):args+=['--'+key,str(R/c[key]),'--'+key+'-sha256',c[key+'_sha256']]
 code=main(args);p=B/'runs'/c['id']/'result.json';result=json.loads(p.read_text());labels=result.get('requirements',[]);results.append(dict(id=c['id'],expected=c['expected'],actual=labels,matches=labels==[dict(id='R1',status=c['expected'])],response=result.get('response'),result_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
with (B/'controls-result.json').open('x') as out:json.dump(results,out,indent=2);out.write('\n')
print('Controls:',[(r['id'],r['matches']) for r in results])
