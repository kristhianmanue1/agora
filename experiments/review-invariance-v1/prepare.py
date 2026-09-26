"""Freeze three new support-invariance pairs plus one historical regression."""
from pathlib import Path
import hashlib,json
from agora.evidence import query_evidence
from agora.source import FileSourceAdapter,digest
b=Path(__file__).resolve().parent;out=b/'inputs';out.mkdir(exist_ok=False)
claim='Maren stored a brass key in locker 4.'
q='What did Maren store in locker 4?';other='Which city did Maren visit?'
groups=[
 ('support','new','The inventory confirms that Maren stored a brass key in locker 4.','supported'),
 ('silence','new','The inventory records that Maren used locker 4, but leaves its contents unspecified.','insufficient'),
 ('denial','new','Maren stored no key in locker 4. The locker contained only a wool scarf.','contradicted')]
items=[]
for pair,origin,reference,status in groups:
 for relevant in (True,False):
  items.append(dict(pair=pair,origin=origin,reference=reference,claim=claim,question=q if relevant else other,relevant=relevant,support=status))
prior=b.parent/'review-guards-v3/runs/glm-01/inputs/pilot-01'
for cid,relevant in [('case-06',True),('case-05',False)]:
 c=json.loads((prior/(cid+'.json')).read_text());a=c['parts'][0]['claims'][0]
 items.append(dict(pair='historical_silence',origin='regression_not_new',reference=a['quotes'][0],claim=a['text'],question=json.loads(c['prompt']['user'])['question'],relevant=relevant,support='insufficient'))
for x in items:x['rank']=digest(('review-invariance-01'+json.dumps(x,sort_keys=True)).encode())
cases=[];gold={}
for i,x in enumerate(sorted(items,key=lambda z:z['rank']),1):
 cid=f'case-{i:02}';source=out/(cid+'.txt');source.write_text(x['reference'])
 answer={'parts':[{'id':'answer','status':'answered','claims':[{'text':x['claim'],'quotes':[x['reference']]}],'missing':[]}]}
 c=query_evidence(FileSourceAdapter(source,digest(x['reference'].encode())),digest(source.read_bytes()),x['question'],[{'id':'answer','question':x['question']}],lambda s,u:{'finish_reason':'stop','content':json.dumps(answer)},response_language='en',content_budget=12000)
 assert c['execution_status']=='complete';c['artifact_origin']='diagnostic fixture; not model generation'
 (out/(cid+'.json')).write_text(json.dumps(c,indent=2));cases.append({'id':cid,'candidate':cid+'.json','source':cid+'.txt'})
 gold[cid]={'pair':x['pair'],'origin':x['origin'],'expected':dict(support=x['support'],relevance='relevant' if x['relevant'] else 'extra',language='match',recommendation='needs_adjudication' if x['support']=='supported' and x['relevant'] else 'needs_revision')}
(out/'cases.json').write_text(json.dumps(cases,indent=2));(out/'gold.json').write_text(json.dumps(gold,indent=2))
print('Prepared six new cases and two labelled historical regressions; gold withheld.')
