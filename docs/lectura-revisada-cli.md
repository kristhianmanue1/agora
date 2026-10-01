# Lectura y revisiones explícitas desde la CLI

Entrada común: `python3 scripts/agora_issues.py --workspace RUTA ...`.
Crear workspace una vez con `init`. Cada salida debe tener ruta nueva. No hay bucle
automático ni admisión de memoria. Los comandos se ejecutan deliberadamente.

## Recorrido

1. `retrieve-subquestions` y `generate-plan` preparan y generan la primera lectura.
   Para un candidato existente, comenzar por el paso 2.
2. `review-rubric-scoped` revisa cobertura con la distinción de alcance v2.
3. `review-fidelity` contrasta con Jev las afirmaciones y sus propias citas.
4. `reading-route` verifica los vínculos y devuelve la siguiente acción.
5. Sólo si devuelve `expand`: `coverage-plan` prepara más pasajes y
   `generate-recovery` produce un derivado. Volver a los pasos 2–4 con su hash nuevo.

Los comandos anteriores `review-rubric` y `generate-plan` conservan contratos.
`coverage-plan` acepta explícitamente revisión v1 o v2; no cambia las etiquetas
históricas ni convierte contradicted en missing por regla local. Propuestas ligadas
a otro hash de implementación requieren preparación nueva, no migración silenciosa.

### Revisiones

```bash
python3 scripts/agora_issues.py --workspace RUTA review-rubric-scoped \
  --source FUENTE --source-sha256 HASH_FUENTE \
  --candidate CANDIDATO --candidate-sha256 HASH_CANDIDATO \
  --rubric RUBRICA --rubric-sha256 HASH_RUBRICA \
  --question 'PREGUNTA' --part-id P1 --live --out REVISION_NUEVA

python3 scripts/agora_issues.py --workspace RUTA review-fidelity \
  --candidate CANDIDATO --candidate-sha256 HASH_CANDIDATO \
  --live --out FIDELIDAD_NUEVA
```

La primera usa GLM (`ZAI_API_KEY` o `SKOPOS_LLM_API_KEY`), máximo 2.048 tokens de
salida. La segunda usa `TYPESAFE_API_KEY`, modelo solicitado `jev-1.13.0`, preguntas
choice. Ambas: una llamada, 90 segundos, sin retry. Credenciales por entorno o un
launcher como Llavero; no poner claves en argumentos ni archivos de resultados.
Para replay sustituir `--live` por `--response ARCHIVO_RESPUESTA`.

### Decisión sin proveedor

```bash
python3 scripts/agora_issues.py --workspace RUTA reading-route \
  --source FUENTE --source-sha256 HASH_FUENTE \
  --candidate CANDIDATO --candidate-sha256 HASH_CANDIDATO \
  --rubric RUBRICA --rubric-sha256 HASH_RUBRICA \
  --review REVISION_NUEVA/result.json --review-sha256 HASH_REVISION \
  --fidelity FIDELIDAD_NUEVA/result.json --fidelity-sha256 HASH_FIDELIDAD \
  --question 'PREGUNTA' --part-id P1 --can-expand --out RUTA_NUEVA.json
```

`--can-expand` declara disponibilidad de otra lectura; no prueba que exista evidencia
nueva ni autoriza llamadas automáticas. Omitirlo si no se dispone de otra lectura.
La ruta exige la revisión scoped v2 y la revisión de fidelidad vinculada al candidato.
Recalcula etiquetas desde respuestas conservadas y compara la solicitud de fidelidad.
Los hashes acreditan vínculos, no autenticidad criptográfica del proveedor ni verdad.

| Decisión | Acción |
|---|---|
| expand | Preparar ampliación explícita con presupuesto y conservar el original |
| insufficient_evidence | Faltan requisitos y no se declaró otra lectura disponible |
| requires_coverage_inspection | Hay contradicción o incertidumbre; inspeccionar antes de ampliar |
| requires_fidelity_inspection | Alguna afirmación/ausencia no recibe respaldo suficiente |
| stop_inconclusive_review | Falló o no terminó una revisión; no interpretar como aprobación |
| candidate_ready_for_explicit_review | Rúbrica cubierta y dictamen favorable de fidelidad; sigue sin admisión |

## Distinciones y límites

- “No encontrado en los pasajes” no equivale a “no existe en la fuente”. El nuevo
  prompt clasifica el requisito ausente como missing, sin certificar la ausencia.
- `gaps` distingue referencia fuera del contexto de referencia presente pero omitida
  por la respuesta. Es una comprobación de rangos exactos, no prueba de que no haya
  evidencia equivalente en otro pasaje ni adjudicación semántica independiente.
- Una afirmación factual incompatible con evidencia, o una negación global falsa,
  sigue siendo contradicted. No se remapea automáticamente a missing.
- Jev evalúa afirmaciones contra sus citas y ausencias contra el contexto leído;
  cobertura y fidelidad siguen siendo ejes distintos.
- Las revisiones no demuestran que la rúbrica sea suficiente ni completitud global.

Los límites son por operación; este recorrido manual no implementa una cuota global
persistida entre todos los comandos. Los experimentos fijan sus máximos por separado.
Una interrupción puede dejar attempted: inspeccionar antes de una nueva operación,
no repetir a ciegas. Fuentes de revisión hasta 160.000 bytes. Markdown/JSONL aquí
son texto UTF-8; no se añadió parser semántico JSONL ni extracción PDF/Word.

## Evidencia

[Controles y segunda lectura](../experiments/scoped-flow-v1/README.md),
[fuentes nuevas y formatos](../experiments/scoped-generalization-v1/README.md).
Se corrigió también la comparación de planes léxicos serializados: la reconstrucción
se normaliza a arrays JSON, manteniendo comparación de todos los campos y hashes.
