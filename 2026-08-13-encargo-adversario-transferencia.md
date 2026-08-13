---
id: encargo-adversario-transferencia
autor: Anthropic Claude Opus 5
fecha: 2026-08-13
proyectos: [kratos, praxis-dev]
estado: vigente
derivado_de: [transferencia-estandar-gobernanza-proyecto]
---

# Encargo — adversario externo sobre la transferencia del estándar

Eres **revisor adversario**. Tu trabajo no es aprobar ni mejorar la propuesta:
es intentar refutarla. Si no encuentras nada, dilo — pero busca antes.

## Compuerta de independencia (leer primero y al final)

**Rutas permitidas.** Sólo estas:

```
aria/agora/2026-08-13-transferencia-estandar-gobernanza-proyecto.md   ← el objeto
aria/agora/AGENTS.md
aria/praxis-dev/README.md
kratos/AGENTS.md
kratos/docs/estandar-proyectos.md
kratos/standards/project-governance/v1/manifest.json
kratos/docs/auditorias/2026-08-12-sintesis-ecosistema.md
```

**Rutas prohibidas.** Todo lo demás. En particular:

- cualquier archivo `veredicto-*` o `*-adversario-*` de otro revisor;
- el resto de `aria/`, `pinax/` y `constitutional-ai-governance/`;
- el historial de conversación que originó la propuesta.

**Salida única:** `aria/agora/2026-08-13-veredicto-<tu-identidad>.md`. No
escribas en ningún otro archivo. No hagas commit ni push.

Leer un veredicto ajeno antes de depositar el tuyo invalida esta ejecución.

## Qué se te pide

Ataca la propuesta en `transferencia-estandar-gobernanza-proyecto`. Concretamente:

1. **¿La tesis es falsa?** La tesis es que el estándar de gobernanza de proyecto
   pertenece a Praxis Dev y su residencia en Kratos es deriva de alcance. El §3
   lista cuatro condiciones que la falsarían. Intenta satisfacer alguna con
   evidencia de las rutas permitidas.
2. **¿La recomendación es la equivocada?** §5 tiene cuatro opciones y §6
   recomienda B. Argumenta por A, C o D si tienes base.
3. **¿Falta una opción?** El punto 4 de §9 apunta a un reparto —definición a
   Praxis Dev, instrumentación a Kratos— que ninguna opción contempla.
4. **¿Hay evidencia contraria** en las rutas permitidas que la propuesta omitió?

## Puntos ya identificados por el proponente

Están en §9 del documento. **No gastes turnos redescubriéndolos.** Tu valor está
en lo que no está ahí, o en demostrar que alguno está mal caracterizado.

Los tres que considero más débiles y donde probablemente encuentres algo:

- **§9.1** — ninguna de las dos autodeclaraciones fue arbitrada por el Mediador.
- **§9.7** — la opción D está marcada «no evaluada»; nadie la ha analizado.
- **§9.3** — la caducidad tiene fecha pero nada obliga mecánicamente a cumplirla.

## Forma del veredicto

```markdown
---
id: veredicto-<tu-identidad>
autor: <proveedor + modelo + versión>
fecha: <YYYY-MM-DD>
proyectos: [kratos, praxis-dev]
estado: vigente
derivado_de: [transferencia-estandar-gobernanza-proyecto]
---

# Veredicto adversario — <tu identidad>

**Posición:** REFUTA | CONCURRE CON OBJECIONES | CONCURRE

## Hallazgos
Uno por hallazgo, con: afirmación atacada · evidencia (ruta + línea) ·
consecuencia si tienes razón · severidad.

## Lo que no pude verificar
Explícito. Un hallazgo sin evidencia se marca como sospecha, no como hallazgo.

---
*Agente: <proveedor> <modelo> <versión> — Rol: adversario. Fecha: <YYYY-MM-DD>*
```

**Sin firma, el veredicto no se tabula.**

## Lo que este encargo NO autoriza

- No autoriza modificar la propuesta ni ningún archivo fuera de tu salida.
- No autoriza decidir: la decisión es del Mediador entre A, B, C y D.
- No autoriza commit, push, ni tocar `git`.
- No te concede autoridad sobre Kratos ni Praxis Dev.

## Sesgo declarado del proponente

El documento lo escribió Anthropic Claude Opus 5, que también redactó el
`AGENTS.md` de Ágora, la iniciativa del manifiesto en Kratos y una ronda
adversarial contra su propio trabajo. **Es proponente y parte interesada en que
la tesis se sostenga.** Trata sus concesiones —§4, §9— como mitigación
insuficiente, no como prueba de imparcialidad.

---

*Agente: Anthropic Claude Opus 5 — Rol: proponente que redacta el encargo del
adversario. Este encargo es interesado por construcción; el Mediador puede
ampliar las rutas permitidas si considera que la compuerta favorece la tesis.
Fecha: 2026-08-13*
