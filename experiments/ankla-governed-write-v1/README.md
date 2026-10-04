# ankla-governed-write-v1 — Tres sondas para An-KLA

> Parte de la campaña **MemOS contra Ágora, Skopos y An-KLA** (matriz comparativa por función).
> Congelado antes de ejecutar: `cases.json`. Resultados: `result.json`. Laboratorio: `/tmp/ankla-lab-v1` (no se versiona el store).

## Pregunta

¿Qué garantías reales ofrece An-KLA 0.1.0b28 en su función de la matriz — reglas, contratos y vigencia — cuando se ejercita por su CLI gobernado, sin preparación del terreno?

## Resumen ejecutivo

| Sonda | Veredicto | Lo esencial |
|---|---|---|
| P1 Conservación bajo actualización | **PASS** | supersede marca `sustituida` sin borrar: registro físico íntegro, inventario en ambas revisiones, `verify ok` |
| P2 Contratos JSON | **PASS** | 78 contratos con sha256; 3/3 propuestas corruptas rechazadas quirúrgicamente; revisión intacta (cero mutación) |
| P3 Control de vigencia | **PASS con hallazgo** | retrieve devuelve solo lo vigente con exclusión `inactive` detallada; **refute commit inoperable en b28** (exige resolutor externo que ninguna interfaz cablea) |

## Hallazgos que alimentan la matriz

1. **Techo de autoridad derivada**: `model_derived` solo puede commitear representación `summary`; `full` exige autoridad verificada (tool_observed/channel_confirmed). Es una decisión de diseño, no un fallo: la memoria derivada de modelo queda acotada a resumen.
2. **Refutación = máxima garantía**: el contrato existe (propuesta, claim de autoridad, evidencia verificada, attestación del resolutor) pero ninguna interfaz publicada (CLI, MCP) provee resolutor. La refutación queda a la espera de integración de host. Distinguir: no es un bug, es una puerta cerrada a propósito.
3. **Presupuesto de recuperación en bytes** (`--budget`), no en número de resultados — error de operador documentado, no defecto.
4. **Coste**: 0 tokens, ~2 s por ciclo completo de escritura gobernada (plan→autoridad→commit). Contraste directo con la ronda larga: MemOS 16k–35k tokens por respuesta.
5. **Trazabilidad**: cada escritura deja evento de gobernanza firmado; los rechazos son específicos (`supersedes:missing_for_supersede`, `base_revision:not_digest`, `record.id`) — nombres exactos, no códigos opacos.

## Disciplina

- Expectativas congeladas en `cases.json` ANTES de cualquier ejecución material.
- Sin ajuste de terreno: el primer ciclo de escritura falló tres veces por política real (lineage, enum de refs, techo de representación) y se documentó cada rechazo en lugar de sortearlo.
- Los errores del operador se registran como tales.
- MemOS no se re-ejecuta aquí: su columna de vigencia usa la evidencia ya registrada en `scope-vigency-repair-v1` y `memos-long-reserved-v1`.

## Artefactos

- `cases.json` — preguntas y expectativas congeladas
- `result.json` — veredictos y detalle
- `p1-add-v1.json`, `p2-supersede-v2.json` — propuestas válidas
- `p2-c*.json` — las tres propuestas corruptas deliberadas
- `p3-refute-proposal.json`, `p3-refute-claim.json`, `p3-refute-plan.json` — la cadena de refutación y su `skip` documentado
- `commit1.json`, `commit2.json` — decisiones de commit con revisiones resultantes
