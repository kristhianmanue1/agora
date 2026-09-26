# Cobertura global: control conservador antes del juez

## Implementado

La nueva API `agora.coverage.assess_with_coverage` exige `scope="global"` o
`scope="local"`. No clasifica automáticamente preguntas. Devuelve el contrato
separado `agora/coverage-assessment/v0.1`; la API anterior `assess` y las CLI
anteriores conservan su comportamiento y no quedan protegidas automáticamente.

Tras verificar fuente, revisión y envoltorio, calcula los intervalos de bytes
faltantes respecto al original. En alcance global, cualquier hueco devuelve
`global_review_status: blocked_incomplete_context` y
`assessment_status: not_run_incomplete_coverage`, con cero llamadas al proveedor.
El resultado completo describe la finalización de este control, no una respuesta
completa a la pregunta. No existe juicio semántico cuando el modelo no fue llamado.

En alcance local permite evaluar pasajes parciales, pero conserva
`global_review_status: not_requested` y `global_completeness: not_established`.
Con cobertura global completa permite la evaluación, sujeta al presupuesto de prompt,
sin certificar comprensión, verdad ni exhaustividad de la respuesta del modelo.
Siempre conserva `semantic_verification: not_performed`, sin admisión de memoria
ni recuperación automática. El consumidor debe comprobar estados antes de continuar.

```python
from agora.coverage import assess_with_coverage

result = assess_with_coverage(
    adapter, revision, question, envelope_bytes, envelope_sha256,
    provider, scope="global",
)
# Inspeccionar execution_status, global_review_status y assessment_status.
# No convertir judgment.decision en garantía de cobertura o verdad.
```

## Evidencia del 22 de septiembre de 2026

- 128 pruebas locales OK, incluidas nueve del nuevo control. Hay controles positivos
  de contexto completo y negativo de modelo que siempre respondería suficiente.
- Huecos internos, incluso espacios, impiden cobertura total. Intervalos adyacentes
  que cubren todo el original sí cuentan como completos.
- Fuente cambiada y declaración falsificada de cobertura se rechazan antes del modelo.
- Cobertura completa no convierte una generación incompleta en éxito.
- Replay local de la evidencia congelada de `sufficiency-large-v1/runs/glm-01`:
  L3 recuperado, que omitía la cuarta fase, queda bloqueado. Se conserva por separado
  el juicio histórico `sufficient`; no se modifica el experimento original.
- L3 de referencia también queda bloqueado: contiene los hechos necesarios, pero
  sus 285 bytes no cubren el original de 144 748 bytes. Ésta es una restricción
  deliberadamente conservadora, no un fallo semántico de aquella referencia.
- El contexto completo supera los 65 536 bytes permitidos por defecto para el
  prompt; se rechaza antes del proveedor, sin aumentar límites automáticamente.

Tres comprobaciones de replay, **cero solicitudes externas**. Código y script
congelados, 12 archivos, y resultados en
`experiments/coverage-v1/runs/replay-01/` (ignorados por Git).
Hash de results.json:
`b696fcb7e149726edd8a30590228336fc17372f473b687f9b34f8662aec79a74`.
Autorrevisión adversarial del productor; sin revisión independiente en este incremento.

## Límites y siguiente incremento

Este mecanismo comprueba bytes suministrados en un contexto, no secciones entendidas,
relevancia, fidelidad ni la unión de lo leído en llamadas anteriores. Releer todo el
archivo localmente para calcular hashes no satisface cobertura del contexto enviado.
Tampoco basta que un índice declare que se recorrió todo: falta comprobar qué se
preservó entre pasos. Se siguen aplicando los límites actuales del adaptador y
verificador (incluido presupuesto de contenido de 4 MiB de `verify_envelope`).

La nueva API resuelve un bloqueo comprobable, no recupera la cuarta fase ni ejecuta
un resumen global. El siguiente incremento recomendado es un recorrido acotado por
unidades, con revisión fija, registro de unidades procesadas, omisiones y evidencia
retenida. Debe distinguir recorrer la fuente de conservar todo lo necesario para
responder; agotar el presupuesto debe producir un resultado parcial explícito.
Después habrá que conectar este contrato a un consumidor explícito de consultas
globales y probar documentos reales autorizados. Skopos y AN-KLA siguen siendo
integraciones opcionales; no se escribieron sus stores ni contexto canónico.

Sin commit ni push. Los resultados anteriores se conservan intactos.

## Incremento posterior

El [recorrido acotado](recorrido-acotado.md) recuperó las cuatro fases en un ensayo
sintético. Mantiene separadas cobertura de recorrido y conservación semántica;
no sustituye este contrato ni habilita respuestas globales automáticamente.
