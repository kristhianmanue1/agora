# Consulta optativa con evidencia: contrato experimental v1

**Estado:** implementación local experimental, 2026-10-10. **Entrada pública de agentes:** no activada. **Admisión en memoria:** no realizada.

`agora.evidence_answer_flow` compone las capacidades existentes sobre **un archivo UTF-8 completo tal como se entrega**, fijado por SHA-256. El llamador proporciona `source`, `source_id`, `source_sha256`, pregunta, una lista de 1 a 12 requisitos breves, un proveedor inyectable y un directorio de salida nuevo. La CLI sólo ofrece `--live-zai` con `ZAI_API_KEY` o `SKOPOS_LLM_API_KEY` del entorno (inyectable por Llavero) o `--replay-run` de una ejecución completa. Debe comprobarse por separado que está autorizado transmitir el archivo al proveedor elegido. El archivo puede ser un extracto: su hash y la revisión de cobertura no acreditan el PDF o documento original.

```sh
PYTHONPATH=src .venv/bin/python -m agora.evidence_answer_flow \
  --source source.txt --source-id local --source-sha256 HASH \
  --question 'Pregunta' --requirements requirements.json \
  --out /ruta/nueva/run-001 --live-zai --model glm-5.3-flash
```

`requirements.json` es una lista de cadenas. Para replay se pasa sólo `--source`, `--out` y `--replay-run /ruta/run-001`; la pregunta y los requisitos proceden del registro. No se acepta una salida existente. La ruta no está incorporada a `agent_cli` ni cambia las CLI individuales.

## Ejecución y vínculos

1. Se verifica que los bytes de la fuente son regulares, UTF-8, no vacíos, menores o iguales a 160 000 bytes y coinciden con el hash. Se vuelven a leer antes de cada posible despacho. Se envía la fuente entera a `query_evidence` con `citation_mode=ids` y se conserva su `claim-evidence-query/v2` en `candidate.json`.
2. Cuando hay afirmaciones se ejecutan por separado `support` y `relevance` de `split_review`, con su salida en `split-review.json`. Una respuesta sin afirmaciones deja el eje de respaldo en `not_run: no_claims`.
3. `coverage_cli.prepare` exige el mismo hash de fuente y el hash exacto de `candidate.json`. `coverage.json` almacena el juicio global sobre el texto suministrado, no una matriz de cumplimiento por requisito. Si se solicita, `omission_cli.prepare` comprueba también el hash de esa revisión y produce propuestas de omisión en `omission.json`.

`result.json` usa `agora/evidence-answer-flow/v1-experimental`. Enlaza salidas por ruta relativa y SHA-256; identifica fuente, tarea, proveedor y modelo solicitados, número de despachos y presupuesto máximo de cinco. `model_effective` permanece `unknown`: la cadena `reported_model` es la identidad informada por el proveedor, no una comprobación independiente. Cada despacho crea primero `NN-stage-attempt.json` sincronizado en disco con hash de petición lógica, presupuesto, fuente y `remote_outcome=unknown`. La respuesta recibida va a `NN-stage-response.json`. Un error local se registra en `NN-stage-outcome.json`: un HTTP 401 conserva el código sin guardar su cuerpo y se marca `http_rejected`; un timeout deja `remote_outcome=unknown`. En el transporte ZAI, el recibo incluye además el SHA-256 del cuerpo HTTP enviado sin credenciales. No hay reintentos automáticos. Un proceso interrumpido puede dejar sólo el archivo `attempt`; no se interpreta como llamada fallida ni se reenvía.

`candidate_reviewed` indica que terminaron las etapas solicitadas; **no afirma** que todas las afirmaciones sean correctas, relevantes o suficientes. `review_disagreement` indica que cobertura y diagnóstico de omisiones se contradijeron según las reglas observables del contrato; requiere juicio humano. `rejected` significa que el preflight impidió despachos. `incomplete` o `review_incomplete` conservan etapas previas; `remote_outcome_unknown` identifica al menos una llamada cuyo resultado remoto no se conoce. `not_run` indica una etapa no ejecutada. Todos los juicios son consejos: `adjudication=not_performed`, `memory_admission=not_performed`, `disposition=requires_review`.

## Límites y compatibilidad

- La lista de requisitos queda en el prompt y manifiesto; **no existe evaluación independiente por requisito**. Cobertura y omisiones son salidas falibles de modelos, y el diagnóstico puede generar falsos faltantes.
- `split_review` comprueba respaldo contra citas literales y pertinencia frente a la pregunta; no descubre evidencia externa ni demuestra fidelidad semántica de la fuente. La misma configuración de proveedor puede servir a todos los ejes; eso no prueba independencia efectiva.
- `original_document_completeness=not_established` incluso si `supplied_source_coverage=full`. Se excluyen PDF, Skopos, varias fuentes, relaciones entre documentos, vigencia, corrección automática y aceptación institucional.
- Los esquemas v1/v2 de generación y los comandos existentes no se modifican. Un modelo solicitado distinto del informado en el recibo detiene el recorrido y deja ambos valores consultables. El uso/costo sólo puede atribuirse según telemetría recibida; no se deduce facturación.
- El replay exige las peticiones lógicas idénticas, las respuestas grabadas y la misma fuente. Comprueba igualdad de las etapas estructuradas; no repite la inferencia ni demuestra reproducibilidad del proveedor.

La calibración [T0](../experiments/evidence-answer-flow-t0-v1/README.md) y una evaluación reservada T5 siguen siendo puertas antes de incluir esta operación en la entrada pública de agentes. El [plan](plan-consulta-con-modelos-y-evidencia-2026-10-10.md) distingue además PDF y múltiples fuentes como puertas posteriores.
