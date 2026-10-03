# Campaña reservada v2: congelada, sin ejecutar

Dos fuentes QASPER: 68 958 y 45 390 bytes UTF-8, dos preguntas por fuente.
Selección determinista sin consultar respuestas: primeros identificadores no
presentes en los artefactos locales revisados, entre 40 000 y 100 000 bytes.
No se afirma ausencia en entrenamiento del modelo ni representatividad estadística.

`freeze.json` fija hashes, configuración y límites: 14 peticiones HTTP MemOS,
4 generaciones Ágora, cero reintentos, 180 segundos por petición, salida máxima
4096 tokens por respuesta. El límite HTTP no limita las llamadas internas de MemOS;
se medirán por separado. Ágora recibe hasta 12 000 bytes de pasajes por pregunta;
MemOS ingiere la fuente completa una vez. Esa diferencia es parte del mecanismo
comparado, por lo que se contabiliza ingestión además de consultas.

Las etiquetas se mantienen fuera del contexto generador. Se reconstruyen desde
el dataset local fijado por hash y las primeras dos preguntas de cada documento;
el hash de gold.json conserva la identidad de las referencias originales.
Los fallos, abstenciones y rechazos permanecen en el denominador. Se evalúan
omisiones importantes, respaldo, tokens y tiempos; no sólo número de citas.
La comparación con etiquetas externas realizada por el productor no equivale a
adjudicación independiente. No hay resultado de esta campaña todavía.
