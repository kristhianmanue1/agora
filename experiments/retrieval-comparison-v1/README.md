# Comparación offline de recuperación: ninguna variante resuelve los casos

Dos fallos conocidos de recovery-induced-v1; diagnóstico de desarrollo, no reserva
nueva. Cuatro variantes fijadas antes de puntuar: pregunta exacta o sin palabras
funcionales inglesas, combinadas con expansión a tres párrafos siguientes o a
secciones completas. Misma semilla (primer párrafo), top-k 3 y 12.000 bytes.

Las secciones proceden de la estructura de QASPER y se verifican contra los bytes
renderizados; no se infieren a partir de respuestas. Si una sección no cabe, se
conservan los pasajes iniciales que sí caben. Las anotaciones se leen para puntuar
sólo después de seleccionar las cuatro variantes. No hay llamadas a modelos.

| Variante | Modelos: bytes / párrafos anotados | Validación cruzada: bytes / párrafos anotados |
|---|---|---|
| Exacta + párrafos | 9.548 / 0 de 1 | 9.650 / 0 de 3 |
| Filtrada + párrafos | 6.737 / 0 de 1 | 9.650 / 0 de 3 |
| Exacta + secciones | 9.714 / 0 de 1 | 9.345 / 0 de 3 |
| Filtrada + secciones | 6.763 / 0 de 1 | 9.345 / 0 de 3 |

El primer párrafo anotado corresponde a tres requisitos: no son tres recuperaciones
independientes. Cubrir rangos exactos tampoco mide suficiencia semántica: otra
formulación podría respaldar una respuesta. Aquí no generamos nuevas respuestas.

## Diagnóstico y límite de la rúbrica

El párrafo de modelos (bytes 7794–8548) queda en puesto 29 por solapamiento de
palabras de la pregunta exacta; sólo coincide en “models” y “which”. Las tres
líneas anotadas de validación cruzada no comparten términos con la pregunta:
usan xval, strat, block/rand. No reciben puntuación léxica directa. La expansión
por sección probada sigue dependiendo de las mismas coincidencias iniciales y no
resuelve el fallo. Esto sustenta una limitación léxica en estos casos; no demuestra
que los presupuestos sean suficientes para todos los documentos.

Además, la rúbrica del primer caso pide BERT, DistilBERT y RoBERTa, pero su propio
párrafo también menciona GPT-2 y XLNet como modelos autoregresivos empleados.
Por tanto 3/3 en esa rúbrica no demuestra respuesta completa a la pregunta amplia.
La rúbrica congelada se conserva. Una ampliación requerirá versión y evaluación
separadas, no convertir retrospectivamente resultados anteriores en aprobaciones.

## Verificación y decisión

Cuatro tests: presupuesto/UTF-8, búsqueda sin coincidencias, control positivo que
recupera el final de una lista y reproducción exacta de resultados. El baseline
exacta+párrafos reproduce las dos propuestas publicadas anteriormente. Sin cambios
en src ni defaults. La única enmienda mecánica posterior a medición renombró el
módulo experimental para no colisionar con selectors de Python; freeze-initial.json
se conserva y el resultado se reprodujo sin cambios.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/retrieval-comparison-v1/tests.py
PYTHONDONTWRITEBYTECODE=1 python3 experiments/retrieval-comparison-v1/run.py
```

Requiere las fuentes locales y el dataset QASPER de los experimentos previos;
freeze.json fija sus hashes. result.json y diagnosis.json conservan resultados.
No promover ninguna variante. Próxima condición propuesta: recuperación de listas
y encabezados con relaciones de sección, sin limitarse a ampliar las mismas
coincidencias. Comparar contra este baseline antes de consumir API. Evaluar la
completitud de las rúbricas por separado.
