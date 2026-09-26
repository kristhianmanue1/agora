# GLM: aceptación del parámetro frente a cumplimiento del esquema

Observación: 2026-09-23. Ensayo: `experiments/provider-format-v1/runs/probe-01`.

## Resultado

No tratar `response_format.type=json_schema` con `strict=true` como esquema
impuesto por el proveedor en el endpoint probado. Una respuesta HTTP 200,
terminada con `stop`, incumplió tanto un campo requerido como el valor permitido.
El producto no fue modificado; `legacy` sigue siendo el perfil predeterminado.

## Documentación consultada

- [Referencia Chat Completion](https://docs.z.ai/api-reference/llm/chat-completion):
  enumera `text` y `json_object` como formatos admitidos. El texto menciona tres
  valores pero sólo enumera dos; no establece soporte para `json_schema`.
- [Structured Output](https://docs.z.ai/guides/capabilities/struct-output): usa
  `json_object`, describe el esquema en el prompt y valida en el cliente.
  Esa receta no demuestra generación restringida por un esquema del servidor.

## Método congelado antes de ejecutar

Cuatro solicitudes sintéticas independientes, sin historial, herramientas ni
reintentos. Modelo solicitado y reportado: `glm-5.3-flash`. Endpoint:
`https://api.z.ai/api/coding/paas/v4/chat/completions`.
Temperatura 0; máximo 2048 tokens de salida por solicitud; timeout de socket
45 segundos y límite de proceso de campaña 220 segundos. El estado interno del
proveedor, su implementación del formato y los pesos del modelo no son observables.

El esquema exige exactamente `marker` (cadena con enum `schema_ok`) y `quotes`
(lista de cadenas), ambos obligatorios. Los controles positivos solicitan el objeto
válido. Los contraejemplos solicitan `{"marker":"prompt_value"}`. En el caso
`json_schema` el esquema se transmite sólo mediante `response_format`, sin
repetirlo en el prompt. Si el proveedor lo impusiera estrictamente, la respuesta
completada no podría ser ese objeto inválido. El caso `json_object` sirve como
comparación sin contrato de campos.

| Caso | Formato solicitado | HTTP | JSON válido | Cumple esquema | Tokens |
|---|---|---:|---|---|---:|
| json_positive | json_object | 200 | sí | sí | 199 |
| json_counterexample | json_object | 200 | sí | no | 212 |
| schema_counterexample | json_schema, strict | 200 | sí | no | 194 |
| schema_positive | json_schema, strict | 200 | sí | sí | 79 |

Todos terminaron con `stop`. Total: **684 tokens reportados**, **23.284 segundos**
sumando las solicitudes. No es una comparación de rendimiento: hay cuatro casos,
contenidos distintos y caché no controlada.

## Evidencia y verificaciones

`run.py` conserva el ejecutor; `protocol.json` fija casos y criterio de falsación;
`freeze.json` identifica ejecutor y protocolo; `results.json` conserva solicitudes,
contenido final, identificador de respuesta, modelo reportado y uso. No conserva
credenciales ni contenido de razonamiento. `integrity.json` registra verificación
de los archivos congelados y SHA de resultados. Los resultados están excluidos de
Git por el `.gitignore` del experimento. No se publicaron.

Se verificaron sintaxis y tres controles locales del validador: objeto correcto,
objeto con enum incorrecto/campo ausente, objeto con propiedad adicional. Se
contrastaron manualmente las cuatro salidas con el esquema. No hubo cambios en
`src/` ni `tests/`; no se repitió la suite del producto por este ensayo aislado.

## Autorrevisión adversarial y límites

- El positivo con `json_schema` no prueba soporte: el propio prompt basta para
  explicar su resultado. El contraejemplo distingue ese cumplimiento incidental.
- La salida negativa no fue truncada: `finish_reason=stop`. El control positivo
  confirma que servicio, transporte y formato básico funcionaron.
- No se afirma que el servidor ignore internamente el parámetro: se observó
  incumplimiento, no su causa. Tampoco se extrapola a otros endpoints/modelos.
- Cuatro salidas parseables no prueban una garantía universal del modo JSON.
- Ninguna de estas pruebas mide citas literales, abstención, fidelidad o ahorro.
- Revisión del mismo productor; no participó un revisor independiente.

## Decisión técnica y continuación propuesta

Mantener validación local estricta y rechazo de respuestas inválidas. No activar
`json_schema`, no reparar silenciosamente respuestas, no promover `concise-v1` y
no recalcular resultados QASPER anteriores.

El siguiente incremento puede añadir `json_object` como opción explícita del
transporte, desactivada por defecto, y comparar únicamente esa variable con el
mismo prompt, esquema local y modelo. Usar un pequeño conjunto de desarrollo
para detectar regresiones de forma antes de gastar otra muestra QASPER. Medir
validez del objeto, campos requeridos, citas y coste por separado. Si no mejora
la validez del contrato, detener esa línea: JSON válido por sí solo no resuelve
el campo ausente ni las citas no literales observadas previamente.

## Seguimiento

La opción `json_object` ya está implementada, desactivada por defecto. La
[comparación de modo JSON](comparacion-modo-json.md) se detuvo por timeout
tras dos pares completos; todavía no permite recomendar activarla.

## Cierre posterior

Los seis pares pendientes se ejecutaron en una campaña separada. Véase el
[cierre de comparación](comparacion-modo-json-cierre.md): se mantiene el modo
predeterminado; el timeout de la campaña inicial se conserva.
