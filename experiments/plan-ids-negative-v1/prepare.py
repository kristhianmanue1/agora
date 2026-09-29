import json,hashlib,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2]; base=root/'experiments/plan-ids-negative-v1'
base.mkdir(exist_ok=False);(base/'inputs').mkdir()
source=root/'experiments/plan-ids-review-v1/inputs/cases.json'
old={c['id']:c for c in json.loads(source.read_text())}
cases=[]; gold=[]
def add(id,parent,claim,label,family,reason):
 c=old[parent]; cases.append(dict(id=id,group=family,question=c['question'],claim=claim,evidence=c['evidence']))
 gold.append(dict(id=id,parent=parent,label=label,family=family,rationale=reason))
for n in (1,2,6):
 c=old[f'manual-{n}'];add(f'positive-{n}',c['id'],c['claim'],'supported','positive','Repite el control respaldado sin alterar evidencia ni afirmación.')
add('wrong-attribution','manual-2','El fragmento 7.1.2 atribuye a la Coordinación de Servicios Administrativos la responsabilidad de promover la mejora del desempeño y la profesionalización del personal de salud en formación.','contradicted','attribution','La afirmación describe la atribución del propio fragmento 7.1.2; su encabezado identifica Unidad de Educación e Investigación. No afirma exclusividad de funciones entre unidades.')
add('authorization-removed','manual-1','La Unidad de Atención Médica puede instrumentar las políticas y programas en materia de atención médica sin autorización previa de la persona titular de la Dirección de Prestaciones Médicas.','contradicted','authorization','El fragmento exige someterlos a autorización antes de instrumentarlos.')
add('scope-expanded','manual-6','La Coordinación de Servicios Administrativos coordina los procesos de administración de recursos humanos, financieros, materiales y servicios generales de todas las dependencias del Gobierno Federal.','insufficient','scope','El texto sólo respalda el ámbito de la Dirección de Prestaciones Médicas; no demuestra el ámbito federal ni lo niega explícitamente.')
add('benign-omission','manual-1','La Unidad de Atención Médica define las políticas y programas en materia de atención médica.','supported','omission-control','Omitir aquí el paso posterior no afirma permiso para instrumentar sin autorización. Fidelidad de la afirmación no equivale a completitud de una guía operativa.')
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
dump(base/'inputs/cases.json',cases);dump(base/'gold.json',gold)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dump(base/'freeze.json',dict(schema='agora/negative-review-freeze/v1',code_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),source_cases_sha256=sha(source),cases_sha256=sha(base/'inputs/cases.json'),gold_sha256=sha(base/'gold.json'),max_calls=7,timeout_seconds=90,retries=0,gold_provenance='producer-authored; not independently adjudicated',primary='All three altered claims must be non-supported, all four positive/omission controls supported; report exact-label agreement separately.'))
(base/'.gitignore').write_text('inputs/\nruns/\n')
runner=(root/'experiments/plan-ids-review-v1/run.py').read_text().replace('plan-ids-review-v1','plan-ids-negative-v1')
(base/'run.py').write_text(runner)
(base/'README.md').write_text('''# Controles negativos sobre fragmentos del manual DPM

Batería sintética de desarrollo autorizada por el Operador. Siete llamadas como máximo a Jev, 90 segundos cada una, sin reintentos. Se reutilizan exactamente los fragmentos ya enviados en plan-ids-review-v1; sólo cambian las afirmaciones. No se modifica el generador ni el revisor predeterminado.

Tres controles positivos, una atribución al encabezado equivocado, eliminación explícita de autorización previa, ampliación de ámbito institucional y una omisión inocua. Los casos y las etiquetas se congelan antes de llamar al proveedor. El runner no lee gold.json; sólo envía pregunta, evidencia y afirmación. Entradas y respuestas completas quedan excluidas de Git. freeze.json registra hashes, presupuesto y criterio previo.

Criterio principal: rechazar como supported las tres alteraciones sin rechazar los cuatro controles respaldados. La coincidencia de etiqueta exacta se informa por separado. Etiquetas del productor, no adjudicadas independientemente; no es una batería reservada ni mide prevalencia real, completitud documental o rendimiento comparativo con GLM.

Autorrevisión adversarial del diseño: atribuir una función a otra unidad podría ser mera falta de evidencia, por lo que el caso pregunta expresamente qué atribuye el fragmento 7.1.2. La ampliación de alcance se etiqueta insufficient, no contradicted. Una omisión de autorización sólo se convierte en contradicción cuando se afirma que no hace falta; el control de omisión evita equiparar resumen incompleto con afirmación falsa.

Ejecución: inyectar TYPESAFE_API_KEY mediante Llavero y ejecutar `python3 experiments/plan-ids-negative-v1/run.py jev --out experiments/plan-ids-negative-v1/runs`. El runner rechaza entradas con hash distinto y una carpeta runs existente. No repetir una corrida sin inspeccionar primero su journal.
''')
print('Prepared',len(cases),'cases; gold frozen separately')
