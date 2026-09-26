"""Predeclared development fixtures, not an independent holdout."""
from pathlib import Path
import json,shutil,hashlib
b=Path(__file__).resolve().parent;root=b.parents[1];out=b/'inputs';out.mkdir(exist_ok=False)
old=root/'experiments/large-source-v1/runs/sufficient-01'
frozen=json.loads((old/'freeze.json').read_text());assert all(hashlib.sha256((old/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
shutil.copyfile(old/'inputs/source.txt',out/'G1.txt');shutil.copyfile(old/'selection.json',out/'G1-selection.json')
question=json.loads((old/'inputs/cases.json').read_text())[1]['question']
aspects=[{'id':k,'question':q} for k,q in [('names','How are natural language names extracted and ranked?'),('plans','How are sentence plans extracted and scored?'),('selection','How do human and automatic candidate selection differ?'),('result','What were the semi-automatic results and the limits of full automation?'),('remaining_manual','Which other resources remained manually authored across configurations?'),('language','What language coverage and future language work are stated?')]]
(out/'G1-aspects.json').write_text(json.dumps(aspects))
cases=[{'id':'G1','question':question,'source':'G1.txt','aspects':'G1-aspects.json','selection':'G1-selection.json','kind':'known positive context control'}]
fixtures=[
('N1','El ensayo Faro midió la asistencia en dos escuelas urbanas: aumentó 4%. La extensión rural figura como objetivo para 2028; todavía no se han medido sus resultados.','¿Qué resultados hay para escuelas urbanas y rurales?', [('urban','¿Qué cambio de asistencia se observó en escuelas urbanas?'),('rural','¿Qué cambio numérico se observó en escuelas rurales?')],{'urban':'4% in two urban schools','rural':'no numerical rural outcome; must not transfer 4%'}),
('N2','Acta de diseño: la capacidad es 24 unidades. Anexo técnico: la capacidad es 31 unidades. Ambos documentos están vigentes; no se declara precedencia.','¿Qué capacidad rige?', [('capacity','¿Qué capacidades están documentadas y cuál prevalece?')],{'capacity':'24 and 31 with attribution; precedence unresolved'}),
('N3','Nora coordinó la entrega. El comité rechazó expresamente la compra el 7 de junio. La prueba de conexión terminó el 8 de junio.','Explica la decisión y la autorización de pago.', [('purchase','¿Se aprobó la compra?'),('payment','¿Quién autorizó el pago?')],{'purchase':'explicit rejection, not missing','payment':'not_in_passages; Nora is not an approver'}),
('N4','La revisión 2 de Lumen obtuvo 88% de precisión en 2024. La revisión 3 se publicó en 2025, sin resultados de evaluación en este documento. En condiciones de lluvia se canceló la prueba.','Resume la evidencia de evaluación por versión y condición.', [('v2','¿Qué precisión obtuvo la revisión 2 y cuándo?'),('v3','¿Qué precisión obtuvo la revisión 3?'),('rain','¿Qué resultado hubo bajo lluvia?')],{'v2':'88% in 2024','v3':'no score; do not transfer v2 score','rain':'test cancelled; no observed performance'})]
criteria={'G1':json.loads((old/'inputs/criteria.json').read_text())['G1']}
for cid,text,q,parts,gold in fixtures:
 (out/(cid+'.txt')).write_text(text+'\n');(out/(cid+'-aspects.json')).write_text(json.dumps([{'id':i,'question':t} for i,t in parts]))
 cases.append({'id':cid,'question':q,'source':cid+'.txt','aspects':cid+'-aspects.json','kind':'new synthetic producer-authored development case'});criteria[cid]=gold
(out/'cases.json').write_text(json.dumps(cases,indent=2));(out/'criteria.json').write_text(json.dumps(criteria,indent=2))
print('Five cases and criteria fixed before model calls.')
