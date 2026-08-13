---
id: sucesion-y-reparto-del-estandar
autor: Anthropic Claude Opus 5
fecha: 2026-08-13
proyectos: [kratos, praxis-dev, skevi, escrubery]
estado: vigente
derivado_de: [transferencia-estandar-gobernanza-proyecto]
---

# Sucesión y reparto del estándar de gobernanza de proyecto

**Tipo:** propuesta para veredicto independiente · **Decisión:** sin tomar
**Fuentes y partes interesadas:** Kratos, Praxis Dev, Skevi, escrubery · **Decide:** el Mediador

Supersede a `transferencia-estandar-gobernanza-proyecto`, que planteaba la
pregunta equivocada. Per regla 1 de Ágora: **este artefacto es evidencia, nunca
autoridad.**

---

## 0. Qué cambió y por qué

El artefacto anterior preguntaba **quién es dueño de un estándar**, entre dos
partes. Tres rondas lo desmontaron:

| Ronda | Aportó | Efecto |
|---|---|---|
| Revisor externo (opción E2) | «Sucesión, no transferencia» | El espacio de opciones original era falso: no hay artefacto que transferir, hay uno vigente y una dirección futura |
| Auto-adversarial del proponente | Ocho defectos propios, verificados | Esquema YAML inválido, caducidad sin fecha, sede circular, recomendación sobre evidencia sin verificar |
| Revisor externo (ChatGPT) | Dos correcciones sobre evidencia | «Auditado ≠ adoptante»; divergencia con plantilla no es defecto sin invariante incumplido |

Este documento conserva lo acordado y reabre sólo lo que sigue en disputa.

## 1. El objeto podría ser dos objetos

El manifiesto `kratos/standards/project-governance/v1/manifest.json` mezcla dos
familias de reglas:

| Familia | Reglas | Materia de |
|---|---|---|
| **Estructura y tamaños** | `max_lines`, `allowed_root_markdown`, `forbidden_root_globs` | Estándar de diseño de software — Skevi §3.4 |
| **Contrato de agentes** | `dynamic_state_patterns`, requisito condicional AN-KLA, `required_paths` de política | Gobernanza de repositorio — Kratos / Praxis Dev |

**Esto explica por qué varios proyectos pueden reclamarlo con razón: no es un
estándar, son dos en un archivo.** Un corte por capa puede resolver más que un
corte por dueño.

## 2. Cuatro fuentes y partes interesadas

| Parte | Relación con el objeto | Evidencia |
|---|---|---|
| **escrubery** | Origen de facto — **no ha reclamado nada**; sólo necesitaba un gate | Primer `check_sizes.py` del ecosistema, `147dfc0`, 2026-08-07 |
| **Kratos** | Implementación | Manifiesto, niveles L0–L4, `audit`, `init-plan/apply`, autoauditoría `COMPLIANT · L4` |
| **Skevi** | Norma paralela — no reclama el estándar de Kratos, tiene el suyo | §3.4 de su estándar + ADR-001 propio sobre el gate local |
| **Praxis Dev** | Frontera declarada | Tabla de límites de su README, concordante con `kratos/AGENTS.md:3` |

El artefacto anterior consideraba dos. La deliberación estaba mal especificada.

**No todas han reclamado propiedad.** escrubery nunca lo hizo; Skevi tiene norma
propia. Sólo Kratos y Praxis Dev sostienen posiciones sobre este objeto.

## 3. Evidencia verificada

**La frontera Kratos/Praxis la declaran ambas partes, por separado:**

> *«Kratos es el agente de coordinación y conocimiento del ecosistema del
> Mediador.»* — `kratos/AGENTS.md:3`
> *«Praxis Dev: gobernanza ejecutable del proyecto · Kratos: coordinación y
> conocimiento del ecosistema.»* — tabla de límites, `praxis-dev/README.md`

Ninguna fue arbitrada por el Mediador. Son autodeclaraciones concordantes.

**Cronología del gate:**

```
escrubery   2026-08-07   primer check_sizes.py
kratos      2026-08-10   «Añade estándar neutral de proyectos Kratos»
praxis-dev  2026-08-11   repositorio creado
Skevi       2026-08-12   «incorpora el corpus Skevi y política de gate local»
```

Cuatro proyectos formalizaron la misma práctica en cinco días, cada uno por su
lado. **No es deriva acumulada: es un ecosistema que creció más rápido de lo que
pudo declarar sus fronteras.**

**Asimetría de madurez:** Kratos se autoaudita `COMPLIANT · L4`, 14/14 tests;
Praxis Dev está en `0.1.0-draft.1` y la síntesis del ecosistema del 2026-08-12
dice *«Praxis aún no publica nada»*.

**Sujetos externos al ecosistema.** La auditoría del 2026-08-10 aplicó el
estándar a cuatro repositorios —`escrubery`, `ExpertoGobernanza`,
`backupkairos-controller`, `codigocerebro`—, tres de ellos fuera de `aria/`, y
registra una sección *«Correcciones hechas al estándar por evidencia»*. El
estándar evolucionó auditando repos externos, no sólo por declaración.

**Corrección:** una versión anterior concluía que esto vuelve el estándar más
difícil de ceder. **Retirado** — auditar no demuestra adopción, y sin
expectativa contractual demostrada no hay coste de sustitución. Queda como
pregunta para el inventario, no como implicación.

## 4. Hipótesis de trabajo convergentes

Lo siguiente converge entre las tres rondas. **Ninguna fue independiente**, así
que no son consenso: son hipótesis que ningún revisor ha refutado todavía.

1. **Sucesión, no transferencia.** Praxis Dev recibiría dirección futura; Kratos
   conserva autoridad sobre su artefacto vigente hasta que haya sucesor probado.
2. **No existen dos dueños del mismo identificador y versión.** El sucesor tiene
   identidad y versión propias; el anterior se marca `superseded` con digest.
3. **Nada se decide antes del inventario.** Construir compatibilidad sin saber
   quién consume es trabajo especulativo.
4. **No se exige equivalencia funcional** con el motor anterior.
5. **Cada divergencia lleva razón y aprobación**, no se oculta como
   incompatibilidad técnica.
6. **Una fecha incumplida no transfiere autoridad**: produce estado *overdue* y
   obliga a decisión explícita.
7. **Registro en lugar de congelamiento.** Kratos anota capacidades genéricas
   nuevas para el inventario; no se congela una herramienta que funciona a cambio
   de un sucesor que puede cancelarse.
8. **Auditado ≠ adoptante ≠ consumidor operativo.** Son tres señales distintas.
9. **La divergencia plantilla ↔ script vivo no es defecto.** No hay invariante de
   sincronía; la plantilla es activo de inicialización y el script vivo tiene
   extensiones locales legítimas (verificación del bloque AN-KLA). Retirado.

## 5. Lo que sigue abierto

1. **¿El corte va por capa o por dueño?** (§1) Ninguna ronda lo ha decidido.
2. **¿Cuál es el alcance de Skevi?** Su §3.4 y su ADR-001 reclaman la materia de
   estructura. Nadie lo ha confrontado con el manifiesto de Kratos.
3. **Falta ratificación neutral.** Las autodeclaraciones concuerdan; nadie las
   arbitró.
4. **¿Debe existir sucesor?** El inventario puede concluir que no.

## 6. Fase 1 — inventario con señales observables

Buscar declaración de adopción produce un falso negativo: hay **cero**
`.kratos-standard.json` en el ecosistema. Las señales que sí distinguen:

| Señal | Cómo se observa | Qué prueba |
|---|---|---|
| **Dependencia operativa** | El repo invoca `kratos_project.py` o falla sin él | Consumidor real |
| **Configuración declarada** | `.kratos-standard.json` presente | Adopción explícita |
| **Procedencia de plantilla** | El artefacto desciende de `init_assets` | Adopción de facto |
| **Conformidad estructural** | Cumple `required_paths` sin declararlo | Convergencia o adopción silenciosa |
| **Sujeto auditado** | Aparece en una auditoría | **No prueba adopción** |
| **Expectativa contractual** | Otro proyecto asume su existencia | Dependencia latente |

Resultado parcial ya verificable: **escrubery** cumple las cuatro rutas
requeridas sin declararlo; **Skevi** cumple dos y tiene estándar propio, luego no
es consumidor sino norma paralela.

## 7. Resultados posibles del inventario

Los cuatro son admisibles y ninguno es el resultado por defecto:

- **construir sucesor** — Praxis Dev desarrolla la gobernanza transversal;
- **absorber sólo algunas capacidades** — reparto por capa (§1);
- **mantener estándares independientes** — Skevi la estructura, Kratos el
  contrato de agentes, sin sucesor único;
- **no construir sucesor** — el inventario demuestra que no aporta valor.

## 8. Caducidad

- **2026-09-13** — inventario de adopción efectiva y matriz de alcance.
- **2026-11-13** — decidir entre los cuatro resultados de §7.

Una fecha incumplida produce **overdue**, no transferencia por omisión.

## 9. Puntos de ataque que ya identifico

1. **Falta ratificación neutral** — ambas fuentes son autodeclaraciones.
2. **Asimetría de madurez** — el reclamante con frontera declarada no publica nada.
3. **El corte por capa está sin probar** — §1 es una hipótesis del proponente; nadie
   ha verificado que el manifiesto se separe limpiamente en dos.
4. **La reclamación de Skevi no se ha confrontado** — su §3.4 puede o no cubrir lo
   que el manifiesto de Kratos regula. No lo comparé regla por regla.
5. **Sujetos externos sin consultar** — tres repos fuera de `aria/` fueron
   auditados; nadie preguntó a sus responsables si esperan continuidad.
6. **Sede parcialmente circular** — Ágora es neutral por no pertenecer a ninguna
   parte, pero su función viene de la tabla de Praxis Dev.
7. **Todo el linaje es interesado** — la propuesta, sus correcciones y esta
   reescritura las produjo el proponente o revisores que declararon no ser
   independientes. **Ningún veredicto independiente se ha depositado todavía.**

## 10. Qué NO se decide aquí

- No se mueve código ni se cambia la versión de ningún estándar.
- No se repara nada en Kratos: la divergencia plantilla ↔ script queda como
  diagnóstico separado, sin autorización.
- No se decide dónde vive el manifiesto de capacidades.
- No se altera la auditoría de ningún repositorio.

## 11. Criterio de cierre

La deliberación cierra cuando: exista **al menos un veredicto de revisor
independiente** —proveedor distinto al proponente, sin haber leído veredictos
ajenos—; los siete puntos de §9 tengan respuesta o refutación registrada; y el
Mediador decida entre los cuatro resultados de §7.

Un documento aprobado sin objeción depositada no cierra la ronda.

---

*Agente: Anthropic Claude Opus 5 — Rol: proponente. Sin voto, sin tabulación,
sin autoridad de decisión. Este documento incorpora correcciones de dos revisores
externos y de una ronda adversarial propia; ninguna de las tres fue independiente
en el sentido de A4. Fecha: 2026-08-13*
