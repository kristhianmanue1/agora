"""Exercise the public issue CLI against a user-supplied document; no calls here."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
CASES=[
 ('norms','¿Qué órgano aprueba y difunde normas y criterios para la planeación integral de infraestructura médica?', 'La Coordinación de Planeación de Infraestructura Médica aprueba y difunde normas y criterios consensuados para la planeación integral de infraestructura médica.','supported',[170]),
 ('equipment','¿El alcance de la Coordinación Técnica de Equipamiento Médico incluye cocina y comedor?', 'La Coordinación Técnica de Equipamiento Médico excluye de sus funciones el equipo de cocina y comedor.','contradicted',[177]),
 ('cross_sections','¿Cómo se reparten la aprobación de normas de infraestructura y la integración de criterios de adquisición de equipamiento médico?', 'La Coordinación de Planeación de Infraestructura Médica aprueba normas de planeación integral de infraestructura; la Coordinación Técnica de Equipamiento Médico consolida normas y criterios de adquisición de equipo médico, cocina y comedor.','supported',[170,177]),
 ('cover','¿Qué fecha indica el sello de validación y registro de la portada?', 'El sello de validación y registro de la portada indica 19 de diciembre de 2025.','supported_visual_only',[1])]
GLOBAL='Ofrece una visión global de la estructura actual de la Dirección de Prestaciones Médicas: identifica sus unidades y las coordinaciones que dependen directamente de ella, y explica una responsabilidad principal de cada una. Distingue la estructura actual de los antecedentes históricos y señala cualquier información que no esté respaldada por los fragmentos disponibles.'
def cli(*args):
 p=subprocess.run([sys.executable,str(ROOT/'scripts/agora_issues.py'),'--workspace',str(BASE/'inputs/workspace'),*map(str,args)],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return json.loads(p.stdout)
def main():
 source=BASE/'inputs/source.txt';meta=json.loads((BASE/'extraction.json').read_text());assert hashlib.sha256(source.read_bytes()).hexdigest()==meta['source_sha256']
 cli('init');cli('review-init');records=[]
 for cid,question,claim,gold,pages in CASES:
  seed={'schema':'agora/claim-review-input/v1-experimental','question':question,'claim':claim,'evidence':'Manual de Organización de la Dirección de Prestaciones Médicas. Clave 2000-002-001.','provider':'glm','response':{'model':'test-double','choices':[{'finish_reason':'stop','message':{'content':'{"support":"insufficient"}'}}]}}
  initial=BASE/'inputs'/f'{cid}-initial.json';initial.write_text(json.dumps(seed,ensure_ascii=False))
  parent=cli('review-import','--review',cid,'--input',initial)
  path=BASE/'inputs'/f'{cid}-plan.json'
  plan=cli('expand-prepare','--parent',cid,'--expected-parent',parent['sha256'],'--source',source,'--source-id','manual-dpm:2000-002-001','--source-sha256',meta['source_sha256'],'--budget','12000','--top-k','3','--out',path)
  document=cli('expand-inspect','--plan',path,'--expected-plan-sha256',plan['plan_sha256'],'--details')['document']
  spans=document['plan']['envelope']['spans'];selected=sorted({p['page'] for p in meta['page_map'] for s in spans if s['start_byte']<p['end_byte'] and s['end_byte']>p['start_byte']})
  records.append(dict(id=cid,question=question,claim=claim,document_gold=gold,reference_pages=pages,plan_sha256=plan['plan_sha256'],parent_sha256=parent['sha256'],selected_pages=selected,delivered_bytes=document['plan']['envelope']['delivered_bytes'],evidence_bytes=len(document['plan']['evidence'].encode()),ranges=[{k:s[k] for k in ('start_byte','end_byte','sha256')} for s in spans]))
 for record in records:
  record['selected_content_pages']={'norms':[122,170,177],'equipment':[171,177,178],'cross_sections':[146,171,177],'cover':[7,8,9]}[record['id']]
  record['selected_pages_note']='Overlap includes standalone page markers; content pages exclude those markers.'
  record['selected_evidence_gold']={'norms':'supported','equipment':'contradicted','cross_sections':'insufficient','cover':'insufficient'}[record['id']]
  record['criteria_origin']='producer source review; not independent adjudication'
 (BASE/'cases.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
 (BASE/'global-criteria.json').write_text(json.dumps(dict(question=GLOBAL,required_units=['Unidad de Atención Médica','Unidad de Educación e Investigación','Unidad de Planeación e Innovación en Salud','Unidad de Infraestructura, Servicios Médicos Indirectos e Integración Sectorial'],required_direct_coordinations=['Coordinación de Proyectos Especiales en Salud','Coordinación de Servicios Administrativos'],responsibility_pages=[25,87,109,146,182,184],structure_page=18,criteria_origin='producer source review, not independent adjudication'),ensure_ascii=False,indent=2)+'\n')
 for r in records:print(r['id'],r['selected_pages'],r['delivered_bytes'])
if __name__=='__main__':main()
