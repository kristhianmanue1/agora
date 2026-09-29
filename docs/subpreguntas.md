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

La descomposición es manual y explícita. No se interpreta automáticamente un índice, no se ejecuta OCR y este nuevo plan no se acepta silenciosamente como un plan de `expand-evaluate`. El consumidor explícito `generate-plan` ya conecta este plan al generador; véase [generación desde plan](generacion-desde-plan.md). La conexión al revisor no es automática. La fuente puede escanearse localmente varias veces: los bytes entregados no son una medida de trabajo total ni tokens ahorrados.

## Regresión con Manual DPM

En `experiments/manual-dpm-v1/subquestions-results.json`, la consulta compuesta recupera ambos cuerpos de página de referencia (170 y 177), con 5.180 bytes y presupuesto 12.000. La consulta conjunta anterior entregaba 8.315 bytes pero omitía 170.

Para la consulta global, seis cuotas de 2.000 bytes no admiten las seis páginas de referencia completas (cada una supera la cuota). Se entregan candidatos por 6.403 bytes, pero las seis referencias se reportan faltantes. Es una detección útil del límite de la selección, no una solución a la síntesis global. Tampoco demuestra ausencia de todo dato relevante en los candidatos.

Las subpreguntas y referencias se construyeron tras conocer el documento: esto es regresión de desarrollo, no evaluación reservada. El siguiente experimento debería comparar segmentación por funciones y reparto adaptativo bajo el mismo presupuesto, antes de gastar otra llamada global. OCR y revisión visual siguen siendo necesarios para información que no existe en el texto extraído.

## Estrategia optativa por funciones

Añadir `--strategy functions-adaptive` activa un plan `v2-experimental`; el valor predeterminado sigue siendo `paragraphs-equal` y produce el contrato anterior.

La nueva heurística reconoce párrafos de listas numeradas (por ejemplo, `1. Aprobar...`) separados por líneas vacías, incluso con espacios. Adjunta el encabezado numerado local cuando existe y reinicia su asociación al encontrar un marcador de página. No reconstituye funciones partidas entre páginas ni certifica que toda lista numerada sea una función. Sin estructura reconocible devuelve cero candidatos; no cambia silenciosamente al algoritmo anterior.

Cada subpregunta recibe una primera oportunidad con cuota igual. Después usa el sobrante común hasta `top_k` candidatos por pregunta; la unión mantiene el límite total y elimina duplicados. El orden de preguntas puede influir cuando el presupuesto no alcanza; no se garantiza asignación óptima. Las referencias no se usan para puntuar ni seleccionar.

### Resultado local: mismo presupuesto y mismas subpreguntas

| Caso | Párrafos, cuotas iguales | Funciones, sobrante compartido |
|---|---|---|
| Compuesto | 5.180 bytes, páginas 170/177 completas según referencias | 439 bytes, ambas funciones pertinentes y sus encabezados |
| Global | 6.403 bytes, ninguna página de referencia completa | 2.152 bytes, una función y encabezado en cada sección 25/87/109/146/182/184 |

La inspección del productor confirmó que los dos pasajes del caso compuesto expresan aprobación de normas y adquisición de equipamiento. En el global aparecen las seis áreas y una responsabilidad de cada una. Esto es inspección local del productor, no revisión semántica independiente ni síntesis generada. No se verificó la exhaustividad de la estructura organizativa.

**Las referencias originales de páginas completas siguen parciales** en ambos casos con esta estrategia. Se conservaron intactas: llegar a una página no equivale a recuperarla entera. La nueva evidencia es cobertura de funciones concretas inspeccionadas, no aprobación del antiguo criterio de cobertura completa.

Resultados reproducibles: `experiments/manual-dpm-v1/run_functions.py` y `functions-results.json`; planes con contenido permanecen en `inputs/`, fuera de Git. Cinco pruebas adicionales cubren offsets UTF-8, encabezados, presupuesto, redistribución y deduplicación. Se corrigió durante las pruebas un error al combinar intervalos representados como listas y tuplas. No hubo llamadas a proveedores.

Continuación ejecutada: [conexión y evaluación](generacion-desde-plan.md); la respuesta real fue rechazada por citas no literales. El plan mantiene `global_completeness=not_established`; ninguna reducción de bytes autoriza afirmar exhaustividad.
