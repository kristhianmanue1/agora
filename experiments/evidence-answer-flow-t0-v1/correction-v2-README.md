# Corrección v2 limitada a los B fallidos de T0

**Estado inicial:** perfil y selección congelados antes de llamadas nuevas. El T0 original conserva su denominador de seis y su resultado B de 3/6. Esta corrección es otra serie; no sobrescribe recibos ni convierte un fallo original en éxito retroactivo.

El [congelado](correction-v2-freeze.json) vincula el resultado de la serie `run-2026-10-10-glm-paired-02-llavero`, el [perfil](correction-v2-profile.json), siete archivos de implementación y los únicos B seleccionados: `case-03`, `case-04` y `case-06`. El ejecutor verifica los seis casos base y las fuentes de los tres seleccionados antes de red. Cada salida va a un directorio nuevo; no hay reintentos ni llamadas para A, 01, 02 o 05.

Cambios deliberados respecto al perfil B original:

- El prompt de generación pide JSON sintácticamente completo, como máximo seis afirmaciones y dos IDs por afirmación, preservando matices y declarando `partial` cuando esos límites impidan completar la respuesta. El límite validador de 12 citas **no aumenta**.
- Respaldo obtiene 4.096 tokens de salida en lugar de 2.048. Pertinencia, generación, cobertura, diagnóstico, modelo solicitado, fuente y máximo de cinco despachos por B conservan sus límites previos.

**Criterio estructural fijado:** las etapas solicitadas de los tres B deben terminar. Se contabilizan también los casos truncados, inválidos o con timeout; un fallo no provoca otro intento en la misma serie. Aun si termina 3/3, el resultado sólo demuestra viabilidad local de este perfil en esos tres textos. Faltan adjudicación semántica, costo comparativo, repetición en muestra nueva y T5 para decidir utilidad. El modelo efectivo y facturación siguen sin verificación independiente.

El `result.json` de la corrección registra hashes de perfil, congelado y código **antes de red**. La revisión original permanece como referencia, y el auditor T0 sigue produciendo 3/6 para su serie.

## Resultado observado, 2026-10-10

La serie separada `correction-runs/run-2026-10-10-failed-slots-v2-01` terminó los tres slots fijados. El [auditor offline](audit_failed_slots_v2.py) comprobó vínculos de fuente, congelado, perfil, código, etapas, intentos y recibos: **9 intentos y 9 respuestas**, todos con `reported_model=glm-5.3-flash`, y **55.695 tokens** acumulados según `usage.total_tokens` reportado. Esas cifras no prueban facturación ni modelo efectivo.

| Caso B | Original | Corrección v2 | Hallazgo estructural |
| --- | --- | --- | --- |
| 03 | `incomplete` | `incomplete` | `finish_reason=length`: los 4.096 tokens de generación fueron reportados como `reasoning_tokens`; contenido vacío. |
| 04 | `review_incomplete` | `candidate_reviewed` | Generación, respaldo, pertinencia, cobertura y diagnóstico terminaron. |
| 06 | `incomplete` | `candidate_reviewed` | Abstención sin afirmaciones; respaldo y pertinencia `not_run`, cobertura y diagnóstico terminaron. |

El criterio fijado de 3/3 **falló**: terminó 2/3. El T0 original permanece 3/6; «cinco casos con alguna ejecución B completa entre dos perfiles» es una observación descriptiva y **no** una tasa de éxito de una sola configuración. No hubo adjudicación semántica cegada de las respuestas ni evaluación de utilidad. La [documentación oficial de Z.AI sobre GLM‑5.3‑Flash](https://docs.z.ai/guides/vlm/glm-5.3-flash) indica que `thinking.type` sólo admite `enabled`; [Thinking Mode](https://docs.z.ai/guides/capabilities/thinking-mode) confirma que no puede desactivarse para esa familia. Una próxima propuesta deberá evaluar una selección explícita de pasajes u otra reducción de complejidad, con alcance de fuente y contrato nuevos, antes de considerar más presupuesto de salida. Nada de esto autoriza promoción o activación.

Reproducción del auditor sin red:

```sh
.venv/bin/python experiments/evidence-answer-flow-t0-v1/audit_failed_slots_v2.py \
  experiments/evidence-answer-flow-t0-v1/correction-runs/run-2026-10-10-failed-slots-v2-01
```
