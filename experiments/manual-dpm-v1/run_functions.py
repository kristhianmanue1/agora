import json,subprocess,sys
from pathlib import Path
b=Path(__file__).resolve().parent;m=json.loads((b/'extraction.json').read_text());results=[]
for case in ['compound','global']:
 out=b/'inputs'/(case+'-functions-plan.json')
 cmd=[sys.executable,str(b.parents[1]/'scripts/agora_issues.py'),'--workspace',str(b/'inputs/workspace'),'retrieve-subquestions','--source',str(b/'inputs/source.txt'),'--source-id','manual-dpm:2000-002-001','--source-sha256',m['source_sha256'],'--spec',str(b/(case+'-subquestions.json')),'--out',str(out),'--budget','12000','--top-k','1','--strategy','functions-adaptive']
 p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
 r=json.loads(out.read_text());record=json.loads(p.stdout);record.pop('output');record['case']=case
 record['selected_content_pages']=sorted({pg['page'] for pg in m['page_map'] for s in r['envelope']['spans'] if s['start_byte']<pg['end_byte'] and s['end_byte']>pg['start_byte']}) if r['envelope'] else []
 results.append(record);print(json.dumps(record,ensure_ascii=False))
(b/'functions-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
