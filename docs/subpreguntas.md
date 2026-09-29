# Recuperación por subpreguntas (experimental)

`retrieve-subquestions` añade preparación local a la CLI existente. No llama modelos, modifica revisiones, admite memoria ni cambia los contratos anteriores.

```bash
python3 scripts/agora_issues.py --workspace /ruta/workspace retrieve-subquestions \
  --source /ruta/source.txt --source-id documento --source-sha256 SHA256 \
  --spec /ruta/subquestions.json --budget 12000 --top-k 1 \
  --out /ruta/plan-nuevo.json
```

El workspace debe estar inicializado (`init`). El archivo de salida debe ser nuevo: no se sobrescribe. La especificación tiene esta forma:

```json
{"schema":"agora/subquestions-input/v1-experimental","questions":[
  {"id":"responsabilidad-a","query":"Pregunta concreta A","reference_ranges":[]},
  {"id":"responsabilidad-b","query":"Pregunta concreta B","reference_ranges":[]}
]}
```

`reference_ranges` admite intervalos UTF-8 `[inicio, fin)` declarados por el usuario/evaluador para comprobar cobertura. Son opcionales como contenido (lista vacía), pero el campo es obligatorio. No guían la búsqueda ni prueban soporte semántico. Se validan contra la identidad exacta de la fuente. Sin referencias, la cobertura se informa como `unknown` aunque haya coincidencias.

El presupuesto total se divide equitativamente entre 1–32 subpreguntas; el sobrante no se redistribuye. Cada búsqueda usa el recuperador léxico existente. La unión elimina duplicados y solapamientos. El paquete final nunca excede el presupuesto compartido. Las cuotas pequeñas pueden descartar párrafos grandes: el informe conserva esos descartes y los rangos faltantes.

## Interpretación del informe

- `candidate_status`: se encontraron pasajes que caben en la cuota, o no. No prueba ausencia de respuesta en la fuente.
- `reference_coverage`: la unión contiene completamente los rangos declarados (`covered`), falta alguno (`partial`) o no hubo referencias (`unknown`). No significa que toda la pregunta esté resuelta.
- `semantic_support=not_verified` y `global_completeness=not_established` siempre: ni los rangos ni las coincidencias léxicas certifican fidelidad o exhaustividad.
- `envelope` conserva texto literal, offsets y procedencia. Contiene datos de la fuente; no debe publicarse sin revisar su alcance.

La descomposición es manual y explícita. No se interpreta automáticamente un índice, no se ejecuta OCR y este nuevo plan no se acepta silenciosamente como un plan de `expand-evaluate`. Conectarlo al generador/revisor exige un consumidor explícito posterior. La fuente puede escanearse localmente varias veces: los bytes entregados no son una medida de trabajo total ni tokens ahorrados.

## Regresión con Manual DPM

En `experiments/manual-dpm-v1/subquestions-results.json`, la consulta compuesta recupera ambos cuerpos de página de referencia (170 y 177), con 5.180 bytes y presupuesto 12.000. La consulta conjunta anterior entregaba 8.315 bytes pero omitía 170.

Para la consulta global, seis cuotas de 2.000 bytes no admiten las seis páginas de referencia completas (cada una supera la cuota). Se entregan candidatos por 6.403 bytes, pero las seis referencias se reportan faltantes. Es una detección útil del límite de la selección, no una solución a la síntesis global. Tampoco demuestra ausencia de todo dato relevante en los candidatos.

Las subpreguntas y referencias se construyeron tras conocer el documento: esto es regresión de desarrollo, no evaluación reservada. El siguiente experimento debería comparar segmentación por funciones y reparto adaptativo bajo el mismo presupuesto, antes de gastar otra llamada global. OCR y revisión visual siguen siendo necesarios para información que no existe en el texto extraído.
