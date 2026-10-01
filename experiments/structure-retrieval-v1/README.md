# Recuperación estructural: mejora localizada con regresiones

Comparación offline sobre cuatro documentos **conocidos**: dos fallos inducidos y
dos casos anteriores. Se consultaron sus encabezados antes de diseñar el selector;
es una prueba de desarrollo informada por los fallos, no generalización independiente.
Parámetros y hashes fijados antes de puntuar; sin cambios tras observar resultados.

## Método

Baseline: pregunta exacta, top-k 3 y tres párrafos siguientes. Variantes:

- `headings`: prioriza solapamiento con encabezado, dando más peso a la sección hoja.
- `headings-lists`: añade coincidencia del cuerpo y presencia de listas cortas;
  prioriza elementos de lista y párrafo precedente dentro de la sección.

Hasta tres secciones, cuotas iguales dentro de 12.000 bytes, sin redistribución.
La semilla es siempre el título. Metadatos estructurales vienen de QASPER, con
renderizado verificado contra la fuente; no hay aquí un extractor general de
estructura desde PDF o transcripciones. Los selectores no reciben respuestas ni
rúbricas. El scoring de anotaciones ocurre después de todas las selecciones.

## Resultado: párrafos anotados recuperados / total

| Caso | Baseline | Encabezados | Encabezados + listas |
|---|---|---|---|
| Modelos preentrenados | 0/1; 9.548 B | 1/1; 2.726 B | 1/1; 2.726 B |
| Validación cruzada | 0/3; 9.650 B | 0/3; 68 B | 3/3; 5.870 B |
| Modelos de referencia | 1/1; 11.492 B | 0/1; 83 B | 0/1; 10.185 B |
| Mitigación de sesgo | 1/1; 7.705 B | 0/1; 3.371 B | 0/1; 3.371 B |

La variante combinada recupera los cuatro párrafos de los dos fallos, pero pierde
los dos aciertos de control. No sustituir el selector actual. El baseline de los
controles se recalcula con la misma semilla y parámetros de esta comparación; no
es la respuesta generada en el experimento histórico.

No hay generación ni nueva revisión semántica. La coincidencia exacta con un párrafo
anotado no demuestra calidad de respuesta y su ausencia no prueba falta de evidencia
equivalente. La rúbrica de modelos continúa incompleta respecto a GPT-2/XLNet;
no se modificó. Los conteos de párrafos tampoco son estimaciones estadísticas.

## Verificación

Cuatro tests: lista positiva, UTF-8/offsets, presupuesto y conservación del título,
cero coincidencias sin declaración de completitud y reproducción de resultados
incluidas regresiones. Cero llamadas a modelos. Sin cambios en producto/defaults.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/structure-retrieval-v1/tests.py
PYTHONDONTWRITEBYTECODE=1 python3 experiments/structure-retrieval-v1/run.py
```

Se requieren dataset y fuentes locales previos; sus hashes están en freeze.json.

## Siguiente condición propuesta

Combinar candidatos léxicos y estructurales, deduplicar rangos y asignar el mismo
presupuesto total; conservar ambos resultados previos como controles de regresión.
No concatenar contextos sin medir el límite ni escoger retrospectivamente el mejor
selector por sus etiquetas. Diseñar y congelar la política antes de puntuar, luego
validarla en fuentes nuevas. Sólo después evaluar una respuesta con proveedor.
