# CLI con dos fuentes nuevas y dos formatos de texto

Fuentes QASPER 1811.04791 y 1712.00733 reservadas por inventario local antes de medir;
no garantía de ausencia de exposición externa o entrenamiento. Fixtures nuevos
Markdown (ventana/rollback) y JSONL (corrección de fecha), sintéticos sin personas
ni operaciones reales. Se leen como UTF-8 crudo, sin parser documental nuevo.

Todos usan retrieve-subquestions → generate-plan → review-rubric-scoped →
review-fidelity → reading-route. Presupuesto 20.000 bytes, top-k 4; generación del
consumidor existente hasta 8.192 tokens, revisión 2.048, una llamada por fase.

## Defecto encontrado y corrección

Primera condición: los cuatro planes léxicos fueron rechazados antes de API, porque
la reconstrucción tenía tuplas donde el JSON serializado tenía listas. Se conservan
cuatro resultados con cero HTTP. La corrección compara la representación JSON de
la reconstrucción con el documento: mismos campos y hashes, sin retirar validaciones.
Un test confirma que modificar rangos sigue rechazándose antes de llamar al proveedor.

La condición fixed-freeze.json empezó después de corregir ese defecto, con las mismas
fuentes y criterios; cuatro intentos previos conservados, ninguna llamada de proveedor
repetida. No se ajustaron rúbricas, presupuestos ni respuestas tras observar salidas.

## Resultados de la condición corregida

| Caso | Cobertura scoped | Jev | Ruta |
|---|---|---|---|
| QASPER medidas intrínsecas | 2/2 | supported | Candidato para revisión explícita |
| QASPER VQA | 1/2 | supported | Evidencia insuficiente; no se declaró ampliación |
| Markdown sintético | 2/2 | supported | Candidato para revisión explícita |
| JSONL sintético | 1/1 | requires_review | Inspección de fidelidad |

En JSONL las dos afirmaciones fueron supported, pero la declaración de información
faltante recibió insufficient. No se declara causa sin explicación del revisor ni
se repara automáticamente. Cubrir la rúbrica no fuerza aceptación de la respuesta.

Doce llamadas, 24.608 tokens reportados. Sin precio monetario medido, repeticiones
estadísticas ni adjudicación independiente. Resultados mixtos preservados; no se
promueve fiabilidad general. Los datos completos en inputs/runs* son locales y
excluidos de Git; reportes conservan respuestas y hashes. verify.py comprueba la
reproducción, la normalización del plan y el vínculo de revisiones/citas/decisión.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/scoped-generalization-v1/verify.py
```
