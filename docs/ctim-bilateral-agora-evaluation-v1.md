---
id: ctim-bilateral-agora-evaluation-v1
autor: Codex
fecha: 2026-10-09
proyectos: [agora, expertoGobernanza, skopos]
estado: borrador
derivado_de: [intercambio-evidencia-fuentes-v1]
---

# CTIM bilateral: aporte incremental y evaluación de Ágora v1

**Estado:** contrato de preparación. El preflight del consumidor observado el
2026-10-09 está en `repair`; esta especificación no congela ni ejecuta N1–N5,
no llama modelos y no promueve una relación a memoria. Su propósito es hacer
medible el aporte de Ágora cuando el productor ya pueda entregar pasajes
localizados de los siete originales.

## Frontera entre productor y consumidor

Skopos conserva la captura y recuperación: fuente, manifiesto de derivación,
respuesta de página, modalidad y líneas. Ágora sólo consume archivos ya
producidos mediante `agora.skopos_page_bridge`. El puente rechaza cambios de
manifiesto, derivación, página, modalidad, línea o `item_id`; luego
`source_evidence_exchange` verifica el literal, rango, SHA y, si se suministra
el original local, su SHA-256. Ninguno de esos pasos prueba fidelidad visual,
cobertura global, autenticidad del productor, sentido de una relación o
vigencia.

No se copia un índice, corpus, runtime o política de Skopos. El resultado de
Ágora es un paquete local de evidencia y, opcionalmente, una relación
**candidata**. `candidate_unreviewed`, `semantic_support=not_verified` y
`admitted=false` son resultados correctos de este contrato. Una relación
admitida requiere una decisión y mecanismo de admisión fuera de v1.

## Entrada mínima por fuente

Para cada uno de los siete originales, el productor debe entregar una ruta de
lectura comprobable y su recibo. Para PDF, es una respuesta operativa de página
y el manifiesto exacto que la describe; para HTML, un selector o rango de bytes
del original y el manifiesto/recibo que lo fija. La entrada a Ágora por pasaje
contiene:

1. original local, `source_id`, SHA-256, medio y revisión declarada;
2. respuesta `page` y manifiesto de Skopos; y
3. para PDF, al menos un `item_id` más página, `bbox` y modalidad; para HTML,
   selector o rango de bytes y, cuando exista, el `item_id` del productor.

El puente crea en un directorio nuevo `derived.txt` y `exchange.json`. El
validador debe ejecutarse con `--original`; sin `original_integrity=sha256_verified`
el pasaje no cuenta para el preflight. Para HTML, el consumidor debe crear un
intercambio con rango de bytes o selector y cotejarlo contra el original; el
puente de página es específico de PDF.

## Medición por N1–N5

La batería conserva sus preguntas y casos; esta tabla define sólo el producto
adicional y la medida de Ágora. No prescribe contenido de respuesta.

| Caso | Producto incremental de Ágora | Regla de medición | No demuestra |
|---|---|---|---|
| N1_FLOW | Pasaje o bundle localizado; relación sólo si la pregunta realmente requiere varias fuentes | Pasajes con SHA original verificado, literal y página/offset; si hay bundle, fuentes distintas | flujo institucional verdadero |
| N2_LEVEL | Bundle candidato con anclajes de función, sección o actividad | Número de anclajes tipados y fuentes distintas; huecos conservados | nivel, jerarquía o autoridad |
| N3_VERSION | `version_relation_candidate` sólo con literal de transición y soporte documental para `supersedes`/`amends` | Dos fuentes con fechas declaradas, literal de transición localizado y predicado declarado | vigencia jurídica o texto consolidado |
| N4_NAMES | `identity_unresolved_candidate` salvo prueba externa revisada | Menciones separadas, hashes y localizadores conservados | que dos nombres designen la misma unidad |
| N5_UNSUPPORTED | Paquete de evidencia inspeccionada sin relación, o resultado de cobertura insuficiente | Fuentes/pasajes inspeccionados y motivo de no generar candidato | ausencia en el corpus o abstención correcta del modelo |

En v1, «memoria jerárquica» sólo significa que cada paquete puede ser una
unidad L0 trazable para una transformación posterior. No se consolida L1–LN,
no se escribe AN-KLA y no se admite memoria durante la comparación. La medida
de ese eje es cero admisiones y cero escrituras; convertir paquetes en memoria
es un experimento posterior, con autoridad separada.

## DoD y decisión

El preflight queda en `run` sólo si cada condición tiene un recibo fechado:

1. siete de siete originales verificados por SHA y tamaño;
2. siete de siete fuentes descubribles mediante la misma operación documentada
   del productor, sin que Ágora seleccione una ruta especial;
3. para cada pregunta, los pasajes usados pueden convertirse y validarse con
   `original_integrity=sha256_verified` y localizador físico/byte explícito;
4. los controles de la sección siguiente producen el resultado esperado; y
5. se registran minutos de preparación, número de búsquedas/páginas, bytes de
   derivados, pasajes rechazados y tiempo de revisión humana.

Si falta una ruta de lectura comprobada para alguna fuente, el resultado es
`repair`; no se aumenta el presupuesto del otro brazo ni se sustituye el
faltante por una inferencia. Esa ruta puede ser prederivada o bajo demanda, y
su costo se registra. Si la integridad o el alcance fallan, es `stop`. Sólo el
consumidor decide `run`.

## Controles obligatorios

| Control | Sonda | Resultado esperado | Atribución |
|---|---|---|---|
| Positivo de ruta | Pasaje real con `item_id` presente en su manifiesto | puente crea intercambio y el validador verifica original | Skopos produce; Ágora valida |
| Negativo de integridad | Modificar un byte del original o usar SHA distinto | `original_sha256_mismatch` | Ágora |
| Negativo de productor | Cambiar texto, página o hash del manifiesto en la respuesta | rechazo del puente | Ágora frente a artefacto Skopos |
| Negativo de localizador | Referencia fuera de segmento o `item_id` inexistente | rechazo, sin salida parcial | Ágora |
| Negativo de relación | Usar una forma de relación no admitida, o declarar una relación estructuralmente válida pero semánticamente no revisada | la primera se rechaza; la segunda permanece `not_verified` y no admitida | Ágora |
| Caso sin relación | Un pasaje suficiente para responder sin enlazar fuentes | se conserva como evidencia; no se fabrica `cross_source_candidate` | Ágora |
| Control de no-ejecución | Ejecutar validación/bridge sobre recibos ya guardados | `provider_calls=0`; no se inicia Skopos ni modelo | Ágora |

Un control negativo sólo cuenta si su positivo correspondiente pasó con los
mismos límites y archivos de referencia. Los controles de relación no prueban
una relación; prueban que Ágora no la promueve.

## Registro compacto de coste

Por fuente y por caso registrar: `source_sha256`, estado de cobertura,
`original_integrity`, cantidad de páginas/HTML inspeccionado, bytes del
derivado, cantidad de pasajes aceptados/rechazados, duración de preparación y
duración de revisión. Por ejecución registrar versión del puente, hash del
manifiesto productor, comando/recibo de origen y `provider_calls` de Ágora.
No usar tokens como costo equivalente ni atribuir al modelo minutos gastados en
extracción o revisión.

## Estado observado y siguiente acción

El preflight `ctim-comparison-next-preflight-2026-10-09.json` reporta
originales 7/7 íntegros, pero descubrimiento/lectura neutral de siete fuentes,
controles bilaterales y costos comparables siguen sin demostrarse. Los perfiles
PDF parciales son evidencia histórica de cobertura limitada, no prueba de que
la lectura bajo demanda sea imposible. Por ello este contrato actualmente
produce `repair`, no resultados N1–N5. La siguiente acción autorizada es que
el productor exponga y pruebe su recuperación neutral; después el consumidor
puede ejecutar los controles y decidir si la batería se congela.
