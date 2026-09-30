# Diagnóstico experimental de omisiones

`diagnose-omissions` propone qué información falta y conserva evidencia localizable. No repara el candidato ni admite memoria. Requiere una revisión review-coverage terminada, ligada por hash a la misma fuente, candidato, parte y pregunta. También admite revisar un candidato calificado complete para contrastar falsos completos; la etiqueta previa no se envía al modelo.

```bash
python3 scripts/agora_issues.py --workspace /ruta/workspace diagnose-omissions \
  --source /ruta/fuente.txt --source-sha256 HASH_FUENTE \
  --candidate /ruta/candidato.json --candidate-sha256 HASH_CANDIDATO \
  --part-id P1 --question 'Pregunta global' \
  --review /ruta/revision/result.json --review-sha256 HASH_REVISION \
  --response /ruta/respuesta.json --out /ruta/diagnostico-nuevo
```

Sustituir `--response ...` por `--live` para una llamada explícita GLM, mediante Llavero como en la [guía de suficiencia](revision-suficiencia-cli.md). Por defecto 2.048 tokens de salida; `--max-output-tokens 4096` permite un presupuesto explícito mayor. Timeout 90 s y cero reintentos. El presupuesto se registra en el informe y no altera el prompt. El directorio debe ser nuevo. Fuentes de hasta 160.000 bytes, candidato/revisión de hasta 8 MiB, prompt de hasta 200.000 bytes; sin truncamiento silencioso.

El modelo recibe pregunta, candidato y unidades de evidencia con IDs. Devuelve:

```json
{"status":"proposed_omissions","omissions":[{"missing":"Información propuesta como faltante","evidence_ids":["ev_ID_DEL_REQUEST"]}]}
```

Máximo ocho propuestas y cuatro IDs por propuesta. Las alternativas no_omission_found y uncertain exigen lista vacía. El código rechaza IDs inexistentes o repetidos, forma inválida y salida truncada. Resuelve cada ID al texto literal y offsets UTF-8 start_byte/end_byte (fin exclusivo) del archivo fijado por hash. No acepta offsets inventados por el modelo.

El resultado conserva missing, evidencia y estados semantic_support=not_verified y absence_from_candidate=not_verified. La pertenencia literal está comprobada; que el fragmento respalde lo propuesto, que falte en el candidato y que sea necesario para la pregunta requieren contraste semántico. No_omission_found tampoco prueba exhaustividad.

Siempre disposition=requires_review. review_disagreement señala conflictos entre complete y propuestas, o entre omitted y no_omission_found; no resuelve cuál tiene razón. No hay escritura en ledger de pendientes, AN-KLA ni reparación automática. Se reservan request.json/result.json antes de red. Ante fallo o interrupción, inspeccionar el registro; no repetir a ciegas ni reutilizar el destino.

## Estado de validación

[Prueba real](../experiments/omission-cli-v1/README.md): localizó dos omisiones conocidas y propuso dos adicionales. El control con una respuesta suficiente se truncó y quedó rechazado. Por ello la validación semántica está **parcial**: aún no hay evidencia de ausencia de falsos faltantes en ese control. Diez pruebas específicas y regresión verifican mecanismos, no fiabilidad semántica.

[Condición posterior de 4.096 tokens](../experiments/omission-cli-budget-v2/README.md): ya no hubo truncamiento, pero el control suficiente devolvió JSON con un carácter sobrante y quedó rechazado. Su texto propone dos posibles omisiones adicionales; la expectativa de ausencia de omisiones requiere revisión. Validación aún parcial, sin reparación automática.
