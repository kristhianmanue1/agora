# Subpreguntas: comparación local sin generación

## Resultado

Separar etiquetado y predicción ayuda a recuperar el etiquetado con presupuesto
pequeño, pero **no supera 2/4 párrafos** del plan manual. El caso sigue sin selección
automática suficiente frente a esa referencia. No se modifica el algoritmo.

| Consulta | Presupuesto | top_k | Bytes entregados | Párrafos completos | Bytes de referencia |
|---|---:|---:|---:|---:|---:|
| Unificada limpia | 5.000 | 3 | 4.708 | 0/4 | 0 |
| Unificada limpia | 5.000 | 6 | 4.968 | 1/4 | 577 |
| Unificada limpia | 12.000 | 3 | 5.315 | 0/4 | 0 |
| Unificada limpia | 12.000 | 6 | 10.897 | 2/4 | 1.162 |
| Dos subpreguntas | 5.000 | 3 | 4.748 | 1/4 | 585 |
| Dos subpreguntas | 5.000 | 6 | 4.928 | 1/4 | 585 |
| Dos subpreguntas | 12.000 | 3 | 9.886 | 2/4 | 1.162 |
| Dos subpreguntas | 12.000 | 6 | 11.168 | 2/4 | 1.162 |

Las consultas inglesas, fijadas antes de ejecutar, preguntan por recogida/mapeo de
etiquetas y por predicción entrenada. El control unificado concatena exactamente
las dos preguntas. No incluye instrucciones de respuesta ni términos de la solución
como Transformer. Las consultas fueron redactadas por el productor después de
conocer este documento: no son evaluación reservada.

En `paragraphs-equal`, dividir también divide la cuota: cada pregunta recibe la
mitad del presupuesto total, sin redistribuir sobrantes. top_k limita semillas por
pregunta; la expansión a vecinos permanece activa. No atribuir diferencias sólo a
la redacción: también interviene la asignación de cuota propia del algoritmo.

## Diagnóstico de ranking

`ranking.json` conserva las posiciones de los párrafos que contienen los rangos
manuales. Para la consulta de predicción, los párrafos de arquitectura y mecanismo
quedan en posiciones **11 y 12**, con cinco coincidencias cada uno. No entran entre
las primeras 3/6 semillas. El objetivo de satisfacción queda en posición 5.

Las coincidencias incluyen palabras frecuentes inglesas (`the`, `from`); el filtro
actual de palabras frecuentes es principalmente español. También usa tokens exactos,
sin resolver variantes morfológicas. Esto identifica limitaciones del método, pero
no demuestra que una única modificación resuelva toda la recuperación.

## Evidencia y límites

Ocho configuraciones congeladas; una fuente conocida, SHA-256 verificado. Rangos de
referencia excluidos de la entrada del selector y usados sólo para puntuación.
Control positivo 4/4 con selección manual, negativo 0/4 con selección vacía. Se
comprueban presupuestos y localización UTF-8. Se escanea toda la fuente localmente.
Bytes fuera del plan manual no se clasifican automáticamente como irrelevantes.
La cobertura por párrafos no equivale a suficiencia semántica exhaustiva.

Cero llamadas API, cero tokens nuevos, sin cambios al código del producto ni
pruebas nuevas de MemOS. Los tiempos individuales no se presentan como rendimiento
estadístico. La revisión de resultados es del productor, no independiente.

## Reproducción

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/subquestion-comparison-v1/run.py \
  --repo "$PWD" --source /ruta/1901.05415.txt --out /tmp/subpreguntas-nuevas
```

El script exige salida nueva; genera los ocho planes y sus métricas. `freeze.json`
contiene consultas, presupuestos y hashes. Los rangos manuales provienen del plan
explícito publicado. `ranking.json` es un diagnóstico posterior a la prueba,
calculado por coincidencias de tokens y desempate por orden de fuente, como el
recuperador; no se utilizó para retocar las consultas congeladas.

## Próximo incremento recomendado

Probar, como alternativa optativa, un ranking que descarte palabras frecuentes del
idioma de consulta y dé más peso a términos discriminativos. Compararlo con esta
línea base y con documentos no usados para ajustarlo; conservar también consultas
en español para no ocultar el límite entre idiomas. No aumentar top_k hasta obtener
un pase ni introducir términos de la respuesta manualmente. Sólo volver a generar
cuando la selección entregue la evidencia pertinente bajo presupuesto.
