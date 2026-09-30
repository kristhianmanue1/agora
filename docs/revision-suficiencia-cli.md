# Revisión experimental de suficiencia

`review-coverage` evalúa si un candidato responde una pregunta frente al archivo fuente completo suministrado. Es una opción explícita; no cambia el revisor predeterminado, no revisa fidelidad y no admite memoria. Incluso coverage=complete conserva disposition=requires_review.

## Entrada

Requiere workspace inicializado, fuente UTF-8 y candidato `agora/claim-evidence-query/v1` o `v2` con execution_status=complete. Acepta los candidatos por IDs producidos por generate-plan. Se selecciona una parte por su ID y se entrega explícitamente la pregunta global que se quiere evaluar. La pregunta se conserva en el informe; no se infiere ni se reescribe una intención ambigua.

Los hashes son SHA-256 hexadecimales de los bytes exactos de fuente y candidato. La revisión comprueba ambos, la revisión fuente declarada por el candidato y la forma/citas de la parte seleccionada. Eso no certifica su verdad ni procedencia externa. Límite: 160.000 bytes de fuente, 8 MiB de candidato y 200.000 bytes de prompt; no trunca silenciosamente. Se usa EvidencePolicy predeterminada para validar la parte.

## Uso

```bash
python3 scripts/agora_issues.py --workspace /ruta/workspace review-coverage \
  --source /ruta/fuente.txt --source-sha256 HASH_FUENTE \
  --candidate /ruta/candidato.json --candidate-sha256 HASH_CANDIDATO \
  --part-id P1 --question '¿Qué modelo utilizaron?' \
  --response /ruta/respuesta-guardada.json --out /ruta/revision-nueva
```

La respuesta de replay tiene forma:

```json
{"finish_reason":"stop","content":"{\"coverage\":\"complete\"}"}
```

Para ejecución real, sustituir `--response ...` por `--live`. Usar Llavero, con intérprete y script absolutos:

```bash
python3 /Users/krisnova/www/aria/llavero/llavero.py ejecutar zai -- \
  /usr/bin/python3 /Users/krisnova/www/aria/agora/scripts/agora_issues.py \
  --workspace /ruta/workspace review-coverage \
  --source /ruta/fuente.txt --source-sha256 HASH_FUENTE \
  --candidate /ruta/candidato.json --candidate-sha256 HASH_CANDIDATO \
  --part-id P1 --question '¿Qué modelo utilizaron?' \
  --live --out /ruta/revision-nueva
```

Una solicitud glm-5.3-flash, temperatura 0, JSON, máximo 2.048 tokens de salida y timeout 90 s. Sin reintentos ni red en replay. Los criterios e instrucciones coinciden exactamente con la configuración experimental congelada; una prueba lo comprueba.

## Salida y recuperación

El directorio debe ser nuevo. Antes de enviar se conserva request.json y result.json con status=attempted. Al terminar, result.json registra origen live/replay, hashes, pregunta, configuración, respuesta/uso reportado y etiqueta. Las opciones son complete, omitted, justified_abstention y uncertain. Se conserva la etiqueta cruda; no es una decisión de aceptación.

Código de salida 0 significa revisión registrada, no que el candidato haya sido aceptado. Rechazo local o fallo devuelve 2. Un timeout preserva failed; una interrupción puede dejar attempted. **No repetir a ciegas:** el estado remoto puede ser desconocido. El comando rechaza reutilizar el directorio. Crear otro directorio no constituye comprobación de que el primer envío no ocurrió.

Los informes son archivos separados; no se insertan automáticamente en el ledger de pendientes ni se recuperan mediante su subcomando recover. Esta primera integración conserva trazabilidad local y rechaza repetición del destino; no proporciona recuperación transaccional general.

El informe declara fidelity=not_assessed, adjudication=not_performed, memory_admission=not_performed y source_completeness=not_established. Este último campo recuerda que un archivo íntegro puede proceder de una extracción incompleta. El prompt usa la fuente completa suministrada, no una garantía de que falten cero páginas, tablas u OCR.

## Evidencia y límites

[Ensayo CLI](../experiments/coverage-cli-v1/README.md): replay, rechazo local, diez pruebas específicas, regresión y una revisión real de candidato conservado. [Batería congelada](../experiments/coverage-heldout-v1/README.md): 14/14 controles del productor en seis documentos. Persiste un error previo ante pregunta ambigua y no existe adjudicación independiente general. No usar complete como verdad, revisión clínica o permiso de ejecución.
