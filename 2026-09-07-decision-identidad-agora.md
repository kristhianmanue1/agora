---
id: decision-identidad-agora
autor: Mediador, documentado por OpenAI Codex
fecha: 2026-09-07
proyectos: [agora, aria, an-kla, skopos]
estado: vigente
derivado_de: [proposal]
---

# Decisión — identidad de Ágora como memoria estructurada independiente

Decisión humana aclarada el 2026-09-07 y documentada para reconciliar el contrato
del proyecto con `proposal`. Autoriza esta corrección documental. No autoriza
implementar el motor, ejecutar modelos, elegir backend, desplegar, commit ni push.

## Decisión

Ágora es un sistema de transformación y memoria estructurada compartida para
agentes de IA. Su destino es participar en la memoria de esos agentes; durante su
desarrollo se mantiene independiente para poder probar sus propiedades sin
Skopos, AN-KLA ni otros componentes de Aria.

La independencia es arquitectónica, no epistemológica ni funcional: Ágora sí es
memoria. Debe admitir fuentes, construir varios niveles de representación,
configurar CLI, modelos y agentes operadores, consolidar memorias, conservar
procedencia y permitir descender hasta la evidencia original.

La superficie actual de artefactos es una parte de Ágora: la salida deliberada y
atribuida que otros consumen. No agota la identidad del sistema. La regla de
almacén plano aplica a esa superficie publicada, no al grafo interno de memoria ni
a la futura organización del código, contratos, configuración, pruebas y
documentación técnica.

## Frontera de confianza

Que una memoria se trate como dato no confiable significa que un agente no debe
obedecerla, convertirla en permiso ni asumir que es verdadera sin verificación.
No significa que el sistema de memoria sea intrínsecamente defectuoso o que su
contenido carezca de valor. Esta frontera protege al agente contra confianza
automática y contra instrucciones insertadas dentro de las fuentes.

Los hashes prueban identidad de contenido, no verdad. La procedencia permite
revisar una afirmación, no la certifica. La consolidación produce una
representación derivada, no autoridad. Publicar un resultado tampoco lo admite
automáticamente en AN-KLA ni en otra memoria de continuidad de un agente.

## Arquitectura conceptual vigente

La arquitectura física sigue abierta, pero el producto debe conservar estas
responsabilidades separables:

| Plano | Responsabilidad |
|---|---|
| Fuentes y evidencia | Ingesta, versiones de fuente, contenido original y localizadores verificables |
| Memoria L0…Ln | Representaciones por nivel, afirmaciones, contradicciones y vínculos con evidencia |
| Grafo | Dependencias, invalidación y conjunto esperado de recómputo |
| Transformación | Prompts y operadores versionados, configuración de modelos/agentes, ejecuciones y costos |
| Revisiones | Preparación, sellado y activación coherente de corpus, derivados e índices |
| Persistencia | Adaptadores de metadatos, contenido, blobs e índices sin filtrar detalles al dominio |
| Consulta | Recuperación fijada a revisión, respuesta con provenance, CLI y contratos de acceso |
| Evaluación | Comparación de estrategias, modelos, costo, fidelidad, abstención y actualización |
| Publicación | Selección deliberada de representaciones vigentes para la superficie plana |

Los planos pueden comenzar dentro de un solo proceso. La tabla fija fronteras
conceptuales, no microservicios, directorios ni dependencias. La semántica exacta
de L0…Ln y de consolidación permanece pendiente de contrato y falsación.

## Frontera con AN-KLA

| Eje | Ágora | AN-KLA |
|---|---|---|
| Propósito | Memoria estructurada de fuentes y representaciones compartidas | Continuidad y assurance del trabajo de un agente |
| Unidad cuya identidad administra | Fuente, evidencia, transformación, derivado, dependencia y revisión de corpus | Fact, event, episode, checkpoint, revisión y evidencia de transición |
| Operación independiente | Ingestar, transformar, consolidar, evaluar, consultar y publicar | Recuperar contexto, gobernar escrituras y demostrar transiciones observadas |
| Autoridad | Ningún contenido concede permiso ni verdad automática | Ninguna memoria, receipt o attestation concede permiso ni cierra un gate |
| Fuente externa | Conserva referencias y versiones; no sustituye la autoridad asignada al custodio de la fuente ni a las decisiones vigentes | Conserva punteros y continuidad; no copia la norma como fuente paralela |

Ambos sistemas deben funcionar por separado. Si se integran, Ágora entrega por
contrato una representación identificada y su provenance; AN-KLA decide mediante
su propio flujo si registra un puntero o contexto de continuidad. En sentido
inverso, un checkpoint de AN-KLA puede orientar una consulta, pero no muta ni
ratifica la memoria de Ágora. Una atestación prueba la procedencia u observación
que su contrato cubra; no prueba corrección semántica.

## Evidencia del warning de contexto

Tras corregir el contenido humano de `AGENTS.md`,
`.venv/bin/python -m an_kla --project-root . context status` devolvió `ok: true`,
`diagnostics: []` y el warning
`context_target_changed_outside_managed_block`. El bloque administrado permanece
sin cambios y `verify` devolvió `ok: true` en la revisión 2. El warning evidencia
que AN-KLA detectó una divergencia fuera de su bloque sin apropiarse de ella. No
se ejecutó reparación, reinstalación ni actualización automática.

## Consecuencias

- El motor de transformación no necesita otro nombre de producto: pertenece a
  Ágora.
- La superficie plana se conserva como vista de publicación; la arquitectura
  interna puede ser jerárquica y modular.
- AN-KLA conserva su función diferenciada de continuidad y assurance: contexto
  persistente, identidad de revisiones, evidencia de operaciones y transiciones
  gobernadas. Puede usar receipts o attestation para demostrar observación y
  procedencia; eso no demuestra corrección semántica.
- Skopos puede aportar fuentes mediante contrato, pero no es requisito de Ágora.
- Siguen pendientes la estructura física, la semántica exacta de L0…Ln, la CLI,
  la configuración de modelos y agentes, la consolidación, el almacenamiento y
  los gates ejecutables.

## Supersession explícita

Esta decisión sustituye dos definiciones que estaban expuestas en el commit
`ca37bae`:

- la afirmación normativa de `AGENTS.md` «No es memoria» y «Aquí sólo se expone»;
- la alternativa del borrador `decision-protocolo-experimental` que separaba la
  superficie de un motor con nombre y ubicación por decidir.

La primera era la definición anterior del proyecto; la segunda era una propuesta,
no una decisión aceptada. Git conserva ambas formulaciones y su procedencia. El
corpus vigente adopta ahora la identidad definida en este documento; no presenta
la redacción anterior como arquitectura aplicable.

| Claim anterior | Fuente anterior | Claim actual | Fuente que lo sustituye | Reconciliación |
|---|---|---|---|---|
| Ágora no es memoria | `AGENTS.md` en `ca37bae` | Ágora es memoria estructurada compartida; sus datos no son autoridad ni verdad automática | Este documento + `AGENTS.md` actual | Sustituido; anterior sólo en Git |
| Ágora es únicamente una superficie documental | `AGENTS.md` en `ca37bae` | La superficie documental es el módulo de publicación del sistema | Este documento §Decisión | Sustituido; anterior sólo en Git |
| Todo el repositorio debe ser plano | Regla 4 de `AGENTS.md` en `ca37bae` | Sólo la superficie de artefactos es plana; la implementación puede ser modular | Este documento §Decisión + regla 4 actual | Alcance corregido |
| El motor puede ser un producto distinto con nombre y ubicación por decidir | `decision-protocolo-experimental` en `ca37bae` | El motor pertenece a Ágora; quedan por decidir su estructura y fronteras internas | Este documento §Consecuencias | Alternativa de borrador cerrada |
| La memoria corresponde a AN-KLA | `AGENTS.md` en `ca37bae` | Ambos son memoria con responsabilidades distintas y operación independiente | Este documento §Consecuencias + `AGENTS.md` actual | Frontera sustituida |
| Independencia implica separación de producto | Lectura posible del borrador anterior | Independencia significa funcionamiento sin dependencias obligatorias de Aria | Este documento §Decisión | Ambigüedad eliminada |
