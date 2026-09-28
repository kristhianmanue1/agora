# Dos variantes ejecutadas; una incompatibilidad contractual — 2026-09-28

## Resultado

| Caso | Conducta observada | Aceptación técnica |
|---|---|---|
| Ausencia sin antecedente | Fecha null/missing; Lina conservada; explicación limitada al fragmento | Rechazado: missing_evidence |
| Contradicción | Fecha null/disputed; ambas fechas citadas; Lina conservada | Aceptado como candidato; partial |

Dos llamadas reales a glm-5.3-flash, mismo identificador reportado por la API.
5582 + 4131 = **9713 tokens** reportados. No hubo reintentos. La primera llamada
terminó con stop: el fallo fue de validación local, no timeout ni fallo de API.
La segunda tardó 54,905 segundos; el runner inicial no guardó duración al fallar
la validación, por lo que no se declara latencia total.

El primer runner se detuvo ante el rechazo estructural antes del segundo caso.
continue_conflict.py ejecutó únicamente el caso independiente no intentado,
verificando hashes del congelado original. No se editó la respuesta ni se
relajó el validador histórico. Ambas evaluaciones fueron en frío, sin antecedente
ni evaluación previa. La fecha retenida no apareció en el request de ausencia.

## Hallazgo y corrección propuesta

El contrato v3 exige evidence no vacía para todos los campos. Para ausencia pura,
no existe una cita afirmativa sobre la fecha. GLM devuelve evidence=[] y explica
correctamente el alcance de la búsqueda. El validador rechaza esa representación.
Citar «Lina es responsable» cumpliría forma pero no aportaría soporte de fecha.

Propuesta para un contrato nuevo: separar evidence (citas de afirmaciones) de
reviewed_scope (identidad, versión y localizadores realmente incluidos). Un campo
missing podría carecer de citas afirmativas si conserva alcance revisado verificable;
supported y disputed seguirían requiriendo sus citas. Alcance revisado tampoco
prueba ausencia global. No reinterpretar revisiones v3 ni migrarlas en silencio.

Antes de más llamadas: implementar y probar esa distinción localmente con la
respuesta ya conservada, incluyendo rechazos de alcance inventado y versiones
incorrectas. Después evaluar compatibilidad con el flujo incremental y decidir
una API reutilizable. La corrección no está implementada en esta entrega.

## Evidencia y límites

- Cuatro pruebas locales nuevas: distinguir missing/disputed, exigir ambos lados,
  control positivo de rúbrica y reproducción del rechazo actual. 355 tests pasan.
  El último test conserva una limitación conocida; no la declara comportamiento ideal.
- Cuatro citas del caso contradictorio resuelven a localizadores nativos. SQLite
  recupera los dos paquetes tras reabrir. El caso rechazado permanece en JSON,
  sin revisión SQLite ni admisión.
- Autorrevisión del productor, no revisión independiente. Orígenes con IDs
  distintos no acreditan independencia entre las personas o documentos.
- No se probó orden invertido, variantes lingüísticas ni contradicción posterior
  sobre una evaluación ya guardada. La ampliación positiva fue probada en v1.
- Hay dos scripts porque el primero se detuvo ante un rechazo estructural; esa
  limitación del runner se conserva como parte del ensayo, no se oculta.
- No hubo datos reales, cambios en Skopos, admisión AN-KLA ni despliegue.
