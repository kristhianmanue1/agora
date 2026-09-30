# Candidato real y control: parada por presupuesto de citas

**La comparación no se ejecutó.** La generación respondió con `stop` y JSON válido,
pero el candidato fue rechazado por `part_quote_bytes_exceeded`: 15.062 bytes
resueltos frente al máximo de 12.000 por parte. Se cumplió la parada congelada:
ninguna revisión, ningún reintento ni reparación y ningún cambio de rúbrica.

## Condición

Mismo documento QASPER `1911.10401`, 34.003 bytes y 4.857 palabras. Ahora es un
caso conocido de desarrollo. GLM `glm-5.3-flash` recibió toda la fuente y la pregunta
original, sin rúbrica ni etiquetas. Salida máxima: 4.096 tokens, timeout 90 segundos.
El control del productor menciona sólo SemEval-2018, con expectativas congeladas:
R1 cubierto; R2–R4 omitidos. Su cita contiene los cuatro datasets: prueba deliberada
de que evidencia citada no equivale a información expresada por la respuesta.
El control pasó validación estructural local, pero no fue evaluado por un modelo.

## Diagnóstico reproducido

El candidato incluye seis afirmaciones con once usos de referencias a cuatro
unidades distintas. Al expandir IDs a texto, los usos suman 15.062 bytes; las cuatro
unidades únicas ocupan 5.097. El contrato vigente cuenta cada uso por afirmación.
Por tanto, el rechazo es consistente con el código; no demuestra que el límite
esté mal. El generador recibió esa regla y no la cumplió.

El texto generado nombra los cuatro datasets y declara como faltantes los detalles
de divisiones entrenamiento/prueba. No se infiere cobertura aprobada: no existe
veredicto `review-rubric`, y esa declaración de ausencia tampoco fue adjudicada.
Se preservan respuesta, candidato rechazado y receipt; no se eliminan afirmaciones
ni se rebautiza el candidato como válido.

`python3 experiments/rubric-candidates-v1/verify.py` reproduce el rechazo desde la
respuesta conservada, verifica offsets y hashes, el control local y la ausencia de
la fase de revisión. Cero llamadas durante verificación. Una llamada total a GLM,
10.981 tokens reportados; tiempo del cliente en `result.json`. Coste monetario no
informado. No se modificó producto ni se volvió a ejecutar la suite general.

## Continuación concreta

Preparar una condición derivada explícita: conservar todas las afirmaciones y la
lista de faltantes; retirar referencias secundarias redundantes sólo tras comprobar
el respaldo de cada afirmación. Publicar hashes de original y derivado y la tabla de
referencias retiradas. Validar de nuevo y ejecutar las dos revisiones pendientes.
Es una reparación asistida del candidato, no éxito del generador autónomo. No subir
el límite ni cambiar silenciosamente el cómputo a bytes únicos para hacer pasar
esta salida. El original rechazado y esta parada permanecen como evidencia.

La continuación se ejecutó en una [condición derivada separada](../rubric-candidates-derived-v1/README.md):
las dos revisiones terminaron y coincidieron con las expectativas. Esto no cambia
el rechazo ni la parada de esta condición original.
