---
id: revision-adversarial-m1-r1
autor: Codex con revisores externos GLM y Qwen
fecha: 2026-09-08
proyectos: [agora, skevi]
estado: vigente
derivado_de: [agora-skevi-experiment-v1, agora-skevi-pilot-v1]
---

# Revisión adversarial de M1-R1

## Alcance y límite

Esta revisión cubre el harness experimental derivado del commit M1
`004c7b8b75d2a0506cb9a5867e92ab67049e6305` y corregido hasta
`f6592719d095171de45401d6ee6e13d78eb5c8c0`. El veredicto autoriza tratar
M1-R1 como base para diseñar M2. No autoriza ejecutar productores reales,
reviewers experimentales, fixtures o corridas C0/C1, ni implementa la vertical
slice de Ágora.

## Rondas

| Ronda | Artefacto | Revisor | Verificación | Resultado |
|---|---|---|---|---|
| R0 | `004c7b8` | Codex, mismo linaje autor | Código, Git y ataques ejecutados | Encontró redirección del freeze, metadatos visibles, symlinks, objetos especiales y mezcla outcome/invalidity; no fue independiente |
| R1 | working tree previo a `5ae2699` | OpenCode con `zai/glm-5.2` | Contexto nuevo, fuentes adjuntas, revisión estática | `PROCEED` provisional con dos MEDIUM y tres LOW; sus hallazgos fueron corregidos, por lo que no cerró el resultado final |
| R2 | `004c7b8..5ae2699` | Qwen Code | Contexto nuevo, fuentes y diff; sin ejecución | `FIX-AND-RETRY`: HIGH por pérdida de evidencia durante el sellado; cinco MEDIUM y cinco LOW/INFO |
| R3 | `5ae2699..d1e4665` | Qwen Code | Contexto nuevo, delta exacto; sin ejecución | `FIX-AND-RETRY`: un MEDIUM por código causal falso en invalidity y observaciones LOW/INFO |
| R4 | `d1e4665..f659271` | Qwen Code | Contexto nuevo, delta exacto y lectura del árbol; sin ejecución | `PROCEED`: cero BLOCKER/HIGH/MEDIUM; cuatro LOW residuales |

Claude no produjo revisión por límite de sesión. Gemini mediante OpenCode falló
por credencial inválida. Kimi CLI 0.38.0 falló dos veces con HTTP 500. Cline,
configurado visiblemente con DeepSeek Chat, falló por autenticación. Estos
intentos no cuentan como revisiones ni como evidencia favorable.

## Independencia de la ronda final

| Eje | R4 |
|---|---|
| Independencia del revisor | Externo al autor del cambio |
| Independencia de contexto | Sesión nueva; no se reanudó R2 ni R3 |
| Acceso a fuentes | Delta Git exacto por stdin y lectura del árbol declarada por el reviewer |
| Verificación efectiva | Revisión estática; no reprodujo tests ni comandos |
| Modelo/proveedor | Qwen Code CLI 0.21.13, Alibaba; el ID exacto del modelo no quedó expuesto en la salida final R4 |
| Ambiente | Safe mode y sandbox `permissive-open`; sin delegación, edición o ejecución declaradas |
| Relación con productor | Distinto de Codex y de los modelos productor/reviewer congelados del experimento |

La revisión es independiente respecto de autor y contexto, pero no es una
reproducción independiente de fuentes ejecutables. Las pruebas Seatbelt fueron
ejecutadas por Codex en el host y revisadas estáticamente por Qwen.

## Hallazgos corregidos

- La identidad del lock ahora fija revisión, documentos, digests, secciones,
  condiciones y shape completo; no puede redirigirse a otro corpus y seguir
  informando `ok: true`.
- Manifest, adapter y artefactos fallan cerrado ante lifecycle inválido,
  symlinks, TOCTOU, objetos especiales y exceso real de bytes.
- La política Seatbelt ya no expone metadatos globales y deniega
  `process-info*` salvo self y codesignature necesarios para el runtime.
- `outcome failure` permanece separado de `experimental invalidity`; con
  protocolo inválido el outcome se marca `not_interpretable`.
- Las anomalías posteriores al lanzamiento producen un bundle
  `invalidity_candidate`. Si falla el propio sellado, el staging no se borra:
  se reporta como recuperación, sin declararlo bundle íntegro o finalizado.
- La finalización usa rename exclusivo; la preparación usa link exclusivo.
- El evidence record incluye identidad observable del controlador y degrada a
  `unavailable` sin abortar la preservación.
- Tokens, modelo e invocaciones del productor se declaran
  `unverified_self_report`; M1-R1 no afirma enforcement.
- Los códigos `producer_artifact_changed` y
  `producer_artifact_bytes_exceeded` distinguen integridad de presupuesto.

## Evidencia ejecutada

En `f659271` pasaron 16 pruebas. Tres son integraciones Seatbelt con productor
falso; verifican red denegada, separación C0, ausencia de Git/secretos,
metadatos y process-info bloqueados, señal externa bloqueada, descendientes del
grupo terminados, evidencia sellada, outcome negativo válido y anomalía
post-launch preservada. También pasaron `py_compile`, `verify_freeze.py` y
`git diff --check`. No se llamó a modelos productores ni se ejecutó el piloto.

## Riesgos residuales y gates M2

- No existe cuota de filesystem durante la ejecución.
- No está demostrada la contención de procesos que ejecuten `setsid()` y se
  desacoplen antes de `killpg`.
- Falta un ledger que impida preparación o selección repetida por pair/slot.
- Métricas e identidad del productor requieren receipts observados por el host.
- Artefactos pueden revelar C0/C1 al reviewer; M2 debe medir y registrar esa
  inferencia.
- El execution record no tiene límite propio de tamaño en M1-R1.
- Algunos códigos de error agrupan cambio e ilegibilidad; es una observación
  LOW y no altera el bloqueo.

## Regla para resultados futuros

Todo resultado material sometido al perfil SKEVI requiere una ronda adversarial
fresca sobre su versión final. La revisión debe registrar artefacto, ejes de
independencia, acceso y verificación de fuentes, hallazgos, correcciones,
riesgos y `PROCEED` o `FIX-AND-RETRY`. Si causa cambios, se repite. Una
autorrevisión o una suite verde no se presentan como revisión independiente.

## Veredicto

**PROCEED**, exclusivamente para usar M1-R1 como scaffold al diseñar M2. Las
corridas reales permanecen bloqueadas por los gates anteriores y requieren
freeze y autorización humana separados.
