# Revisión experimental respecto a una rúbrica

`review-rubric` evalúa requisitos suministrados para una pregunta exacta. Es
optativo; no reemplaza `review-coverage` ni `diagnose-omissions`. Un resultado
`all_supplied_requirements_covered: true` significa cobertura según el revisor
respecto a esa lista, nunca exhaustividad de la respuesta o de la rúbrica.

## Entrada

Rúbrica JSON con exactamente estos campos:

```json
{
  "schema": "agora/task-rubric/v1-experimental",
  "source_sha256": "SHA256_HEX_DE_LA_FUENTE",
  "question": "Pregunta exacta",
  "provenance": "Quién la preparó, de dónde deriva y estado de revisión",
  "requirements": [
    {
      "id": "R1",
      "requirement": "Información necesaria para responder",
      "evidence": {"text": "Texto literal", "start_byte": 0, "end_byte": 13}
    }
  ]
}
```

Offsets de bytes UTF-8, fin exclusivo. Se verifica igualdad literal, no que el
pasaje respalde semánticamente el requisito. Entre 1 y 32 requisitos, IDs únicos;
la procedencia es declarada por el llamador, no autenticada. La fuente debe ser
UTF-8, hasta 160.000 bytes. Rúbrica hasta 262.144 bytes; prompt hasta 200.000.
El candidato debe cumplir la validación de citas existente y pertenecer a esa fuente.
La pregunta identifica esta revisión; no acredita cuál fue el encargo original
que produjo el candidato. Cambiar la pregunta exige una rúbrica con nueva identidad.

## Uso

Con un workspace creado mediante `init`, ejecutar:

```bash
python3 scripts/agora_issues.py --workspace "$WORKSPACE" review-rubric \
  --source "$SOURCE" --source-sha256 "$SOURCE_SHA256" \
  --candidate "$CANDIDATE" --candidate-sha256 "$CANDIDATE_SHA256" \
  --part-id P1 --question "$QUESTION" \
  --rubric "$RUBRIC" --rubric-sha256 "$RUBRIC_SHA256" \
  --response "$RESPONSE" --out "$NEW_OUTPUT_DIR"
```

Los hashes son SHA-256 hexadecimales de los bytes exactos. El padre de la carpeta
de salida debe existir; la carpeta de salida no debe existir. Replay requiere
un JSON de respuesta con `finish_reason: "stop"` y `content` como cadena JSON:
`{"requirements":[{"id":"R1","status":"covered"}]}`.
Cada ID suministrado debe aparecer exactamente una vez. Estados permitidos:
`covered`, `missing`, `contradicted`, `uncertain`.

Para una llamada real se sustituye `--response ...` por `--live`, con la credencial
GLM inyectada por el flujo existente de Llavero. Modelo `glm-5.3-flash`, 2.048 tokens
de salida, timeout de 90 segundos, sin reintentos. No se aumenta presupuesto ni se
repara JSON automáticamente. Salida de proceso 2 ante rechazo o fallo.

Se conservan rúbrica validada, solicitud, respuesta recibida y resultado con hashes.
La salida mantiene `requires_review`, `rubric_completeness: not_established` y
`scope: supplied_requirements_only`, incluso si todos los requisitos son cubiertos.
`status: complete` describe la ejecución, no completitud documental. No modifica
el candidato ni admite memoria. La reserva de carpeta evita reutilizar esa salida;
no constituye deduplicación global ni almacenamiento transaccional.

## Verificación de esta integración

493 pruebas locales aprobadas, incluidas 10 del nuevo módulo: vínculos cambiados,
offsets UTF-8, IDs duplicados/desconocidos, truncamiento, fallo sin reintento y
rúbrica deliberadamente incompleta. Recorrido CLI `init` → `review-rubric` con
fuente/candidato reales conservados de QASPER 1803.08419 y respuesta sintética:
0 llamadas HTTP, resultado válido y alcance limitado explícito. Este replay prueba
el cableado y los contratos; no añade evidencia sobre exactitud del modelo.
Antecedente semántico: [12 controles](../experiments/materiality-rubric-v1/README.md),
con etiquetas del productor y documentos conocidos. No es validación independiente.

Siguiente prueba útil: requisitos revisados por otra persona o instancia sobre un
caso reservado, congelados antes de comparar resultados. Evaluar también requisitos
que falten en la rúbrica; el producto no los descubre con este comando.
