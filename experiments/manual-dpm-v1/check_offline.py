import json,sys,subprocess,hashlib
from pathlib import Path
b=Path(__file__).resolve().parent;root=b.parents[1];sys.path.insert(0,str(root/'src'))
from agora.passages import prepare
from agora.source import FileSourceAdapter
cases=json.loads((b/'cases.json').read_text());meta=json.loads((b/'extraction.json').read_text())
body={'norms':[122,170,177],'equipment':[171,177,178],'cross_sections':[146,171,177],'cover':[7,8,9]}
results=[]
def cli(*args):
 p=subprocess.run([sys.executable,str(root/'scripts/agora_issues.py'),'--workspace',str(b/'inputs/workspace'),*map(str,args)],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return json.loads(p.stdout)
for c in cases:
 c['selected_content_pages']=body[c['id']];c['selected_pages_note']='Overlap includes standalone page markers; content pages exclude those markers.'
 c['selected_evidence_gold']={'norms':'supported','equipment':'contradicted','cross_sections':'insufficient','cover':'insufficient'}[c['id']]
 if c['id']=='cover':c['document_gold']='supported_visual_only'
 c['criteria_origin']='producer source review; not independent adjudication'
 plan=b/'inputs'/(c['id']+'-plan.json')
 cli('expand-inspect','--plan',plan,'--expected-plan-sha256',c['plan_sha256'])
 response=b/'inputs'/(c['id']+'-replay.json')
 response.write_text(json.dumps({'model':'test-double','choices':[{'finish_reason':'stop','message':{'content':json.dumps({'support':c['selected_evidence_gold']})}}]}))
 rid=c['id']+'-offline-replay'
 derived=cli('expand-evaluate','--review',rid,'--plan',plan,'--expected-plan-sha256',c['plan_sha256'],'--provider','glm','--response',response)
 parent=cli('review-inspect','--review',c['id'])
 recovered=cli('review-recover','--operation',rid)
 assert parent['sha256']==c['parent_sha256'] and recovered['sha256']==derived['sha256']
 results.append(dict(case=c['id'],derived=derived,parent_unchanged=True,recovery_identical=True,provider_called=False))
(b/'cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n')
(b/'offline-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
q=json.loads((b/'global-criteria.json').read_text())['question']
env,retrieval,prompt=prepare(FileSourceAdapter(b/'inputs/source.txt','manual-dpm:2000-002-001'),meta['source_sha256'],q,'retrieve',content_budget=12000,prompt_budget=65536,top_k=3)
pages=sorted({p['page'] for p in meta['page_map'] for s in env['spans'] if s['start_byte']<p['end_byte'] and s['end_byte']>p['start_byte'] and len(s['text'].strip())>30})
global_result=dict(provider_called=False,answer_generated=False,selected_content_pages=pages,delivered_bytes=env['delivered_bytes'],retrieval=retrieval,ranges=[{k:s[k] for k in ('start_byte','end_byte','sha256')} for s in env['spans']])
(b/'global-retrieval.json').write_text(json.dumps(global_result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(replays=len(results),global_result=global_result),ensure_ascii=False))
