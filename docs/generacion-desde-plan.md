# Generación explícita desde un plan verificado

`generate-plan` consume los planes `agora/subquestions-plan/v1-experimental` y `v2-experimental`. Es un comando nuevo; no migra planes ni revisiones y no admite memoria.

```bash
python3 scripts/agora_issues.py --workspace /ruta/workspace generate-plan \
  --source /ruta/source.txt --plan /ruta/plan.json \
  --expected-plan-sha256 SHA256_DEL_ARCHIVO_PLAN \
  --question 'Resume las responsabilidades presentes en los fragmentos' \
  --out /ruta/directorio-nuevo --live
```

Para replay sin red: sustituir `--live` por `--response /ruta/respuesta.json`. La respuesta guardada debe tener `content` (JSON con parts/id/status/answer/quotes) y `finish_reason`. Se etiqueta `supplied_response_replay`, nunca como ejecución real.

## Garantías acotadas

1. Comprueba hash del archivo y reproduce exactamente el plan contra la fuente fijada; rechaza alteraciones antes de llamar al proveedor.
2. Reserva un directorio nuevo; no sobrescribe. Máximo una llamada GLM (`glm-5.3-flash`, 8192 tokens, timeout de socket 90 s). No hay retry. Credencial `ZAI_API_KEY` o `SKOPOS_LLM_API_KEY`; Llavero exige intérprete absoluto.
3. Envía exclusivamente los pasajes del plan con alcance explícitamente parcial. Reutiliza el consumidor de referencias y el validador de citas literales.
4. Conserva respuesta del proveedor y resultado en `result.json`; `rejected`/`failed` devuelven código 2. La salida puede incluir datos de la fuente: mantenerla local salvo decisión expresa.
5. `global_completeness=not_established`, revisión semántica no verificada y ninguna admisión automática. Cubrir referencias declaradas no prueba exhaustividad.

No es el ledger transaccional de `expand-evaluate`: una interrupción puede dejar sólo el directorio reservado; no se garantiza recuperación de una respuesta que no llegó a guardarse. No interpretar ausencia de resultado como permiso de reenvío ni como coste cero. El timeout no es un límite monetario ni confirma cancelación del lado servidor.

## Ensayo Manual DPM

Una llamada autorizada sobre el plan por funciones: 2.152 bytes de evidencia; 37,179 segundos; modelo reportado `glm-5.3-flash`; 1.171 tokens de entrada y 2.791 de salida (3.962 total).

La salida describió las seis áreas y una responsabilidad por área e indicó alcance parcial, según inspección del productor. **Fue rechazada por `answer_quote_mismatch`**: varias citas colapsaron espacios y saltos de línea. El reporte de coincidencias sólo diagnostica el fallo; no normaliza ni acepta la respuesta. No hubo segunda llamada ni revisión independiente.

La primera invocación devolvió código de proceso 0 con estado JSON `rejected`. Se corrigió el código de salida a 2 para fallos/rechazos y se comprobó con replay, sin repetir la llamada. La evidencia conserva ese resultado anterior y los hashes de la implementación que lo produjo.

Evidencia: [resultado](../experiments/manual-dpm-v1/generation-result.json). La respuesta cruda sigue en `runs/`, ignorada por Git. Próximo incremento: evaluar referencias por identificador usando los mecanismos ya existentes, conservando el rechazo original, antes de relajar fidelidad literal.

## Referencias por identificador

`generate-plan --citation-mode ids` reutiliza `query_evidence`, `build_units` y
`validate_ids`. El valor predeterminado sigue siendo `literal`; no cambia el
contrato de respuestas anteriores. La salida ID usa
`agora/claim-evidence-query/v2`: `parts[].claims[]` contiene texto, IDs y citas
resueltas; `citations` conserva los offsets originales. No es el formato plano
`answer` de la ruta literal.

Cada ID está ligado a identidad de fuente, revisión, offsets y texto. El modelo
selecciona IDs del paquete; Ágora recupera el texto literal sin pedir que lo copie.
IDs desconocidos, de otra revisión o fuera de la selección se rechazan. Los
presupuestos de citas se aplican al texto resuelto, no a la longitud del ID.
Un ID válido demuestra pertenencia y procedencia, **no respaldo semántico**.
Se conservan `semantic_support=not_verified` y
`global_completeness=not_established`.

```bash
# Añadir al comando anterior; mismo plan, fuente, hash y alcance.
--citation-mode ids
```

No se normalizan ni aceptan retrospectivamente las citas rechazadas del ensayo
literal. La evaluación real por ID se registra aparte cuando esté disponible.
