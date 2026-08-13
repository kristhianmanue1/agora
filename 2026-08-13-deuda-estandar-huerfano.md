---
id: deuda-estandar-huerfano
autor: Anthropic Claude Opus 5
fecha: 2026-08-13
proyectos: [kratos, praxis-dev, skevi, escrubery]
estado: vigente
derivado_de: []
---

# Deuda — el estándar de gobernanza de proyecto quedó huérfano

**Tipo:** registro de estado · **Naturaleza:** deuda abierta, sin plan asignado

Per regla 1 de Ágora: **evidencia, nunca autoridad.** Esto describe una
situación; no propone ni autoriza nada.

---

## Qué pasó

El 2026-08-13, por decisión del Mediador, **Kratos retiró de su superficie
activa** el estándar de gobernanza de proyecto y el auditor cross-project:
`docs/estandar-proyectos.md`, `scripts/kratos_project.py` y
`standards/project-governance/v1/` completo. Kratos queda declarado orquestador
final del ecosistema; gobernar la forma de otros repositorios no es su función.

Commit: `b29dde0`. Recuperable en `e11ed5f`.

## La deuda

**El estándar no fue transferido a nadie. Quedó huérfano.**

Precedió a la decisión una deliberación de tres rondas sobre si debía pasar a
Praxis Dev. Ninguna de las opciones deliberadas —statu quo, transferencia
declarativa, transferencia efectiva, fusión, sucesión— fue el desenlace. La
retirada unilateral no estaba en el espacio de opciones.

Eso deja un objeto sin dueño y una pregunta sin responder.

## Dónde está cada pieza hoy

| Pieza | Dónde | Estado |
|---|---|---|
| Norma de estructura y tamaños | **Skevi**, §3.4 de su estándar + ADR-001 | Vigente y propia |
| Implementación local del gate | **escrubery**, desde 2026-08-07 | Vigente, anterior a todo |
| Gate interno | **Kratos**, `check_sizes.py` | Vigente, sólo para sí mismo |
| Gobierno de evidencia de gates externos | **Praxis Dev** | Declarado, sin implementar |
| Manifiesto, niveles L0–L4, auditor | **nadie** | Retirado; sólo en historia de Git |

## Lo que sigue abierto

1. **¿Debe existir un sucesor?** Nadie lo ha decidido. Praxis Dev tiene la
   frontera declarada pero, según la síntesis del ecosistema del 2026-08-12,
   *«Praxis aún no publica nada»*.
2. **¿Convergen las piezas o se quedan independientes?** Que Skevi, escrubery y
   Praxis Dev deban unificarse es **hipótesis, no decisión**. No hace falta
   resolverla para que el ecosistema funcione hoy.
3. **Tres repositorios externos** —`ExpertoGobernanza`, `backupkairos-controller`,
   `codigocerebro`— fueron auditados el 2026-08-10 con una herramienta que ya no
   existe en Kratos. Ser auditado no es adoptar, y no consta expectativa de
   continuidad. **Fuera del alcance del ecosistema; asunto del Mediador.**

## Por qué se registra

Una capacidad que se retira sin sucesor tiende a reaparecer improvisada seis
meses después, en otro sitio y peor. Dejar constancia de que el hueco existe —y
de que existir es intencional por ahora— es más barato que redescubrirlo.

Esta deuda no bloquea nada. No tiene plazo asignado ni responsable. Se cerrará
cuando el Mediador decida si hay sucesor, o cuando se declare que no lo habrá.

---

*Agente: Anthropic Claude Opus 5 — Rol: registro de estado. Sin voto, sin
autoridad de decisión. Fecha: 2026-08-13*
