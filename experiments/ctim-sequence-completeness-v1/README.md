# CTIM 18–22: prueba aislada de respuesta y omisión

**Corte:** 2026-10-10 10:08 UTC. **Resultado:** GLM superó los controles congelados y produjo las cinco actividades con actores correctos en este pasaje; `qwen3:8b` acertó el control negativo, pero produjo ocho falsos faltantes en el positivo y su generación agotó el timeout. La prueba no demuestra capacidad general de Ágora.

## Alcance y procedencia

- Espacio independiente de trabajo: este directorio de `experiments/` en Ágora. No se reutilizó el harness V4c, sus paquetes, prompts, respuestas ni adjudicaciones.
- Fuente primaria: `/Users/krisnova/www/expertoGobernanza/docs/fuentes/imss/2900-003-001.pdf`, página física 15/91, SHA-256 `141d9b090efa4d70799ee1368350a5167347b4e8cd5f99912fb192ce6c704faa`. `source.txt` es **transcripción manual propia cotejada visualmente**, con etiquetas de actor alineadas a actividades. No es extracción automática ni salida de Skopos. SHA-256 de `source.txt`: `db72e2fbb43e100102e39beb1d11a5b09eaafb8df76f2c3c8fbc06c6f131ea66`.
- `freeze.json` fijó antes de llamar modelos pregunta, cinco actividades/actores esperados, control completo, control con actividad 20 retirada y condición de falsación.
- Las tres operaciones por serie usan APIs existentes de Ágora: `query_evidence` para respuesta, `coverage_cli` para revisión y `omission_cli` para diagnóstico. Los controles son respuestas **construidas por el experimentador**, no generaciones del modelo. Cada operación tiene un intento; no hay reintentos ni reparación. El adaptador Ollama sólo está en `run.py`, no en el producto.
- GLM se ejecutó vía Llavero (`zai`) con modelo solicitado `glm-5.3-flash`; las respuestas recibidas reportan ese identificador. Qwen se ejecutó por Ollama local con modelo solicitado/reportado `qwen3:8b`. La identidad efectiva más allá de lo reportado por cada proveedor no se verificó independientemente.
- En Qwen, las CLI experimentales de revisión conservaron `request_config.model=glm-5.3-flash` codificado en producto, aunque el adaptador y las respuestas registraron `qwen3:8b`. El campo `request_config.model` de esas revisiones no describe la petición enviada en esta serie. Esta discrepancia de procedencia debe corregirse antes de integrar un proveedor alternativo en producto; los resultados crudos no se reescribieron.

## Resultados de las series completas

| Señal | GLM `run-2026-10-10-c` | Qwen `run-2026-10-10-d` |
| --- | --- | --- |
| Control completo: revisión / diagnóstico | `complete` / `no_omission_found` (0) | `complete` / `proposed_omissions` (8) |
| Control sin actividad 20: revisión / diagnóstico | `omitted` / 1 propuesta sobre actividad 20 | `omitted` / 1 propuesta sobre actividad 20 |
| Generación desde `source.txt` | `complete`; cinco afirmaciones, 18=CPIM y 19–22=CTIM, citas literales | `failed`, `TimeoutError` a 120 s; no hubo respuesta evaluable |
| Revisión de la respuesta generada | `complete`; diagnóstico propuso 1 matiz de actividad 20 | No ejecutada: no hubo respuesta completa |

El cotejo manual de la generación GLM confirmó orden, actor, acción principal y objeto de 18–22. Su diagnóstico adicional afirmó que la afirmación sobre actividad 20 omitía el propósito de las modificaciones, aunque ese texto constaba en la cita. Ese propósito **no era un campo exigido por la pregunta congelada** (que pidió actor, acción principal y objeto); se conserva como desacuerdo entre herramientas y no como omisión material demostrada. No hubo revisor separado de este agente.

Las ocho propuestas de Qwen para el control suficiente pedían, entre otras cosas, plazos, métricas y mecanismos formales que ni la pregunta ni el pasaje proporcionan. Son falsos faltantes respecto del criterio congelado. El acierto en el control negativo no los compensa.

`audit.py` volvió a cotejar offline hashes de fuente/PDF/freeze, composición de controles, literales y offsets de evidencia, presencia de cinco menciones actividad–actor en GLM y estados conservados. Pasó. Ese chequeo mecánico no valida semántica por sí solo.

## Intentos anteriores conservados

- `run-2026-10-10-a`: proveedor GLM invocado directamente con una variable de entorno presente; las dos revisiones y la generación fallaron con `HTTPError`. Una sonda limitada observó HTTP 401. No cuenta como resultado semántico. No se reusó el directorio.
- `run-2026-10-10-b`: primera serie Qwen; por instrucción posterior del Operador se interrumpió mientras generaba. Los controles que habían terminado se conservan, pero el manifiesto queda `started` y la serie no se cuenta como completa. `run-2026-10-10-d` es una serie nueva solicitada expresamente después de GLM.

## Interpretación y límites

Este ensayo demuestra que **Ágora, con el pasaje correcto suministrado y GLM accesible, pudo responder esta pregunta concreta y detectar una actividad retirada** en los controles. También demuestra que una revisión de cobertura `complete` puede coexistir con un diagnóstico de faltantes discutible, y que el diagnóstico Qwen puede proponer información ausente del propio pasaje. La fidelidad de la transcripción se cotejó visualmente sólo para p15; no se probaron descubrimiento autónomo, lectura del PDF por Ágora/Skopos, vigencia institucional, otras preguntas, repetibilidad entre ejecuciones ni admisión de memoria. La generación, revisión y diagnóstico GLM comparten proveedor; no constituyen adjudicación independiente.

No se modificó código de producto, no se escribió AN-KLA, no se hizo commit ni publicación.

## Reproducción

Los registros completos y solicitudes están en `runs/`; cada ID de run debe ser nuevo. Para comprobar offline los dos resultados conservados:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python experiments/ctim-sequence-completeness-v1/audit.py
```

Para una **nueva** serie GLM, usar Llavero y un ID nuevo desde la raíz de Ágora:

```bash
python3 /Users/krisnova/www/aria/llavero/llavero.py ejecutar zai -- \
  /Users/krisnova/www/aria/agora/.venv/bin/python \
  /Users/krisnova/www/aria/agora/experiments/ctim-sequence-completeness-v1/run.py \
  NUEVO-ID zai
```

Para una **nueva** serie local, con Ollama disponible y `qwen3:8b` instalado:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python \
  experiments/ctim-sequence-completeness-v1/run.py NUEVO-ID ollama
```

Cada nueva ejecución llama al proveedor y puede producir otro resultado; los datos conservados son los observados en las series indicadas.
