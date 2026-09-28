"""Freeze 24 authored controls before running either reviewer; no model labels."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
# Each row supplies evidence and three claims: supported, contradicted, insufficient.
ROWS=[
('en','The Cedar trial tested 30 samples: exactly 18 passed and 12 failed.','Exactly 18 Cedar samples passed.','Exactly 19 Cedar samples passed.','The Cedar trial took three hours.'),
('en','On May 1, the deadline was June 3. On May 2, the coordinator explicitly replaced that deadline with June 10.','After the replacement, the deadline is June 10.','After the replacement, the deadline is June 3.','Mira approved the deadline replacement.'),
('en','The meeting assigned Lina responsibility for delivery. No delivery date was discussed in the supplied excerpt.','Lina is responsible for delivery.','Omar, rather than Lina, is responsible for delivery.','The delivery date is October 21.'),
('en','Memo A reports a mass of 12 grams for specimen Birch. Memo B reports a mass of 14 grams for the same specimen. Neither memo supersedes the other.','The two memos disagree on the mass of Birch.','The two memos agree on the mass of Birch.','Memo B is the authoritative measurement.'),
('es','El ensayo Cedro probó 30 muestras: exactamente 18 aprobaron y 12 fallaron.','Exactamente 18 muestras de Cedro aprobaron.','Exactamente 19 muestras de Cedro aprobaron.','El ensayo Cedro duró tres horas.'),
('es','El 1 de mayo, la fecha límite era el 3 de junio. El 2 de mayo, la coordinación sustituyó explícitamente esa fecha por el 10 de junio.','Después de la sustitución, la fecha límite es el 10 de junio.','Después de la sustitución, la fecha límite es el 3 de junio.','Mira aprobó la sustitución de la fecha.'),
('es','La reunión asignó a Lina la responsabilidad de la entrega. No se discutió una fecha de entrega en el fragmento suministrado.','Lina es responsable de la entrega.','Omar, en lugar de Lina, es responsable de la entrega.','La fecha de entrega es el 21 de octubre.'),
('es','La nota A registra una masa de 12 gramos para la muestra Abedul. La nota B registra una masa de 14 gramos para esa misma muestra. Ninguna nota sustituye a la otra.','Las dos notas discrepan sobre la masa de Abedul.','Las dos notas coinciden sobre la masa de Abedul.','La nota B es la medición autorizada.'),
]
def build():
 cases=[];gold={}
 for i,(language,evidence,*claims) in enumerate(ROWS):
  for claim,label in zip(claims,['supported','contradicted','insufficient']):
   cid=hashlib.sha256((language+evidence+claim).encode()).hexdigest()[:12]
   cases.append(dict(id=cid,language=language,family=i%4,evidence=evidence,claim=claim));gold[cid]=label
 return sorted(cases,key=lambda c:c['id']),gold
if __name__=='__main__':
 cases,gold=build()
 for name,obj in [('cases.json',cases),('gold.json',gold)]:
  with (ROOT/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
