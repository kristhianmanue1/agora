import json,subprocess,sys
from pathlib import Path
b=Path(__file__).resolve().parent;m=json.loads((b/'extraction.json').read_text());raw=(b/'inputs/source.txt').read_bytes()
def reference(page):
 p=m['page_map'][page-1];chunk=raw[p['start_byte']:p['end_byte']];marker=f'[PDF page {page}]'.encode();start=p['start_byte']+chunk.index(marker)+len(marker)
 while raw[start:start+1] in (b'\n',b'\r'):start+=1
 end=p['end_byte']
 while raw[end-1:end] in (b'\n',b'\r'):end-=1
 return [start,end]
compound=[('norms','Coordinación de Planeación de Infraestructura Médica aprobar difundir normas criterios planeación integral',170),('equipment','Coordinación Técnica de Equipamiento Médico consolidar normas criterios adquisición equipo cocina comedor',177)]
global_q=[('care','Unidad de Atención Médica funciones políticas programas atención médica',25),('education','Unidad de Educación e Investigación funciones formación recursos humanos investigación',87),('planning','Unidad de Planeación e Innovación en Salud funciones innovación inteligencia epidemiología',109),('infrastructure','Unidad de Infraestructura Servicios Médicos Indirectos Integración Sectorial funciones',146),('special','Coordinación de Proyectos Especiales en Salud funciones desastres continuidad',182),('administration','Coordinación de Servicios Administrativos funciones recursos presupuesto',184)]
records=[]
for name,items in [('compound',compound),('global',global_q)]:
 spec={'schema':'agora/subquestions-input/v1-experimental','questions':[dict(id=id,query=q,reference_ranges=[reference(page)]) for id,q,page in items]}
 path=b/(name+'-subquestions.json');path.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
 out=b/'inputs'/(name+'-subquestions-plan.json')
 cmd=[sys.executable,str(b.parents[1]/'scripts/agora_issues.py'),'--workspace',str(b/'inputs/workspace'),'retrieve-subquestions','--source',str(b/'inputs/source.txt'),'--source-id','manual-dpm:2000-002-001','--source-sha256',m['source_sha256'],'--spec',str(path),'--out',str(out),'--budget','12000','--top-k','1']
 p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
 plan=json.loads(out.read_text());summary=json.loads(p.stdout)
 summary['reference_pages']=[x[2] for x in items];summary.pop('output')
 summary['queries_origin']='manually decomposed from known document; development regression, not held-out'
 records.append(dict(case=name,**summary));print(json.dumps(records[-1],ensure_ascii=False))
(b/'subquestions-results.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
