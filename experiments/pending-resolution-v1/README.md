# Diagnóstico de los dos pendientes conocidos

Ensayo retrospectivo sobre los casos QASPER y JSONL de scoped-generalization-v1.
No es una evaluación reservada nueva ni una adjudicación independiente. Código
productivo y resultados anteriores permanecen sin cambios.

## QASPER: fallo de recuperación confirmado, ampliación insuficiente

Dos anotaciones humanas preexistentes del conjunto coinciden: Visual7W y una
colección construida de preguntas visuales abiertas. Sus pasajes de evidencia
coinciden literalmente con la fuente fijada. La primera anotación ya se usó para
la rúbrica: este contraste no es ciego ni demuestra independencia del benchmark.

Visual7W no aparece en el contexto inicial. Se ejecutó mediante la CLI una nueva
ampliación conservadora, preservando rangos, pregunta original, límite 20.000 bytes,
top-k 4 y tres párrafos siguientes. La lectura aumentó de 9.334 a 13.168 bytes y
siguió sin contener Visual7W ni los rangos de referencia. La generación volvió a
omitir R1, cubrió R2 por información equivalente y Jev respaldó el contenido
suministrado. La ruta terminó en insufficient_evidence. La fuente sí permite
responder; la lectura seleccionada sigue siendo insuficiente.

Tres llamadas, 13.074 tokens reportados, cero reintentos. Precio no medido. Este
caso refuta que añadir vecinos con la misma búsqueda baste siempre para recuperar
lo importante; no refuta todas las estrategias de ampliación. No se amplió otra vez
ni se introdujo Visual7W como término de búsqueda tras observar la respuesta.

## JSONL: separar respuesta y límite temporal

El registro sintético contiene borrador martes a las 09:00 y corrección miércoles,
con cancelación del martes, a las 09:15. Jev había respaldado ambas afirmaciones;
marcó insufficient únicamente la advertencia sobre cambios posteriores.

Inspección técnica de esta sesión: la respuesta sustentada es «Según el registro
disponible hasta las 09:15, la fecha es miércoles; sustituye al martes, que fue
cancelado». La inexistencia de registros posteriores en esta fuente delimita lo
observado; no demuestra que fuera de ella haya o no cambios. No equivale a una
contradicción real ni permite proclamar una fecha definitiva universal.

Esta formulación es una recomendación, no un candidato admitido ni una reparación
aplicada. Se conservan candidato, revisión y ruta originales. No hubo nueva llamada
para intentar obtener un voto favorable. Falta adjudicación independiente para
cerrar el desacuerdo con Jev; su respuesta no explica la causa de su clasificación.

## Verificación y continuación

verify.py comprueba hashes congelados, anotaciones contra fuente, conservación de
rangos, reproducción exacta de generación y revisiones, y decisión de ruta. Los
artefactos crudos permanecen locales e ignorados; result.json publica evidencia
saneada. La reproducción completa requiere esos artefactos previos locales.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/pending-resolution-v1/verify.py
```

Siguiente experimento recomendado: selección por estructura/sección o descomposición
de la pregunta, con estrategia congelada antes de llamadas, sin términos de las
respuestas de referencia y con controles de regresión. Comparar con lectura completa
y medir coste acumulado. Para el límite temporal, preparar controles de «vigente en
el registro» frente a «definitivo fuera del registro» y adjudicarlos por separado.
No modificar el revisor predeterminado ni automatizar admisión con estos dos casos.
