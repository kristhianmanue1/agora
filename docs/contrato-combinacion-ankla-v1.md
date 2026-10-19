# Contrato de combinación AN-KLA ↔ Ágora: admisión gobernada (v1)

**Estado:** vigente, 2026-10-19. Aceptado por el Operador el 2026-10-19 tras
ejecutar sus puertas de validación: [ensayo en almacén sintético](../experiments/ankla-admission-v1/README.md)
(admisión gobernada, supersede con estados correctos, autoridad falsificada
rechazada con `cli_privileged_authority_unresolved`, cero rutas de escritura
directa en `src/agora` y `verify` con identidad completa). Publicado en
`project-manifest.yaml` como contrato `agora/result-ref/v1`. La referencia
viaja ahora con paquete exportado real: `package_schema` y `package_sha256`
de `agora/consultation-package` se producen y registran en el propio ensayo
desde el 2026-10-19. Ágora sigue
funcionando sin AN-KLA y este contrato no es requisito de ninguna ruta.

## Regla cardinal

**Ágora nunca escribe en el almacén de AN-KLA.** La admisión de un resultado
de Ágora como memoria de continuidad ocurre íntegramente dentro del flujo
gobernado de AN-KLA (`plan-write` → `commit-write-plan` con autoridad y
revisión base exactas), ejecutado por un agente con autorización vigente del
Operador. AN-KLA verifica su propio CAS, sus journals y sus revisiones; Ágora
no los conoce ni los reproduce.

## Objeto de frontera

Lo que cruza es una **referencia**, no una copia:

```json
{"kind": "agora-result-ref/v1",
 "result_id": "r-0007",
 "result_sha256": "<hash del result.json>",
 "package_schema": "agora/consultation-package/v3-experimental",
 "package_sha256": "<hash del paquete exportado>",
 "source_sha256": "<hash de la fuente consultada>",
 "question": "<pregunta exacta>",
 "status": "candidate_reviewed",
 "requires_review": true}
```

Los hashes llegan del [registro de resultados](contrato-consulta-evidencia-v1.md)
y del [paquete de consulta](contrato-consulta-evidencia-v1.md); el id es el del
registro. AN-KLA puede revalidar cualquier hash contra los archivos si le son
accesibles; si no, la referencia declara `unverified_remote_artifact` y no
eleva autoridad por sí misma.

## Qué conserva cada sistema (sin duplicar objetos)

- **Ágora** conserva candidatos, revisiones, evidencia y ejecuciones con sus
  hashes y estados. Sus objetos son inmutables: la corrección produce un
  derivado nuevo, nunca edita el original.
- **AN-KLA** conserva continuidad, identidad de revisiones y evidencia
  gobernada de transiciones. Un fact suyo que refiera un resultado de Ágora
  se sustituye por el flujo gobernado de AN-KLA (`supersede`), nunca
  editando el resultado de Ágora ni regenerándolo.
- Ningún objeto se copia entre sistemas: se referencian por hash. La matriz
  de dominio del proyecto (`AGENTS.md`) se conserva íntegra.

## Autoridad y representación

- Un agente que registra la referencia con autoridad `model_derived` obtiene
  a lo sumo representación `summary`, según la política vigente de AN-KLA.
- `channel_confirmed` requeriría un adaptador del host; nada en este contrato
  lo fabrica ni lo sustituye.
- La referencia nunca silencia memoria vigente: `derived_from_retrieval` no
  puede `supersede`.

## Puertas de validación (fallan cerrado)

1. El resultado referido debe existir en el registro con su hash intacto;
   deriva o borrado bloquean la admisión, no la degradan a advertencia.
2. El estado admitible es explícito: sólo estados terminales documentados
   (`candidate_reviewed`, `rejected`, `remote_outcome_unknown`) cruzan, cada
   uno con su significado; `requires_review` viaja siempre con la referencia.
3. Ningún estado del resultado se traduce a «verdadero» o «aceptado» al
   cruzar la frontera.

## Criterios para pasar de borrador a vigente

1. Prueba del flujo completo en un almacén sintético nuevo, con el mismo
   método del [ensayo de transiciones](../experiments/ankla-transitions-v1/README.md):
   admisión, supersede gobernado y rechazo de escritura directa.
2. Control negativo: un intento de escritura directa desde código de Ágora
   al almacén de AN-KLA queda documentado como rechazado o ausente por
   diseño.
3. Decisión escrita del Operador y publicación del contrato en el manifiesto.

## No-objetivos

Sincronización automática, admisión sin revisión, compactación cruzada,
refundición de las memorias de ambos sistemas o uso de AN-KLA como almacén de
candidatos de Ágora.
