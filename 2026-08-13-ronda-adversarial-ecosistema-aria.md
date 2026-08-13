---
id: ronda-adversarial-ecosistema-aria
autor: Anthropic Claude Opus 5
fecha: 2026-08-13
proyectos: [kratos, praxis-dev, epistates, skevi, argos, escrubery]
estado: vigente
derivado_de: []
---

> **Observaciones fechadas al 2026-08-13.** Parte del contexto envejeció el mismo
> día: Kratos retiró de su superficie activa el estándar de gobernanza de
> proyecto y el auditor cross-project por decisión del Mediador. Las once
> correcciones que este documento registra siguen siendo válidas como registro de
> lo que se afirmó y se retiró; el estado de los repositorios que describe, no.

*Agente: Anthropic Claude Opus 5 — Rol en este acto: auto-adversario. Ataque a mis propias afirmaciones sobre el ecosistema `aria/`, emitidas en sesión el mismo día. Sin rol votante, sin autoridad de decisión arquitectónica.*
*Fecha: 2026-08-13*
---

# Ronda adversarial — Afirmaciones sobre el ecosistema `aria/`

**Status:** Corrección de errores propios. **No es una decisión de arquitectura.** No autoriza crear, fusionar ni renombrar ningún proyecto.
**Authority basis:** Encargo directo del Orquestador en sesión (2026-08-13). Ninguna otra.
**Scope:** Ataque a doce afirmaciones que emití sobre `aria/` tras una inspección superficial. **NO hace:** no propone arquitectura nueva más allá de corregir la que propuse mal, no evalúa nanobot/LightAgent/OpenLaw (no tengo base para hacerlo), no modifica ningún proyecto.
**Owner:** Anthropic Claude Opus 5.
**Estado del árbol:** ningún archivo de `aria/` fue modificado; este documento es el único añadido.

---

## 0. Advertencia

Esto **no satisface A4**. Es el mismo agente atacando sus propias conclusiones: un solo verificador, sin decorrelación. No cuenta como verificación independiente.

Contexto del error: emití una arquitectura completa del ecosistema —reparto de axiomas, regla de secuenciación, recomendación de fusión y luego su contraria— tras una inspección basada en `grep`, listados de directorio y nombres de archivo. Varias afirmaciones no resistieron el primer contraste.

---

## 1. Resultado

Doce afirmaciones atacadas: **cinco retiradas, cuatro corregidas, tres sostenidas.**

| # | Afirmación | Veredicto |
|---|---|---|
| 1 | «Epistates excluye el gateway deliberadamente; lleva cuatro hitos dibujando su silueta por sustracción» | **RETIRADA** |
| 2 | «La exclusión de automatización de epistates no era cautela: era cumplimiento de A0» | **RETIRADA** |
| 3 | «El gateway es la implementación de A0» | **RETIRADA** |
| 4 | «No automatices hasta que exista el gateway, porque automatizar elimina tu canal A0» | **RETIRADA** |
| 5 | «Los contratos ya están escritos; ChronosPraxus no tiene nada que especificar» | **RETIRADA** |
| 6 | «`adapter-capabilities-v1` y `dispatch-receipt-v1` son literalmente la interfaz del runtime» | **CORREGIDA** |
| 7 | «Reusa `scripts/trace/` de CAGF para A6» | **CORREGIDA** |
| 8 | Reparto de compuertas: A0+A9 al gateway, A3+A_Live al runtime | **CORREGIDA** (contradicción interna) |
| 9 | «`agora` es buen nombre para el gateway» | **CORREGIDA** |
| 10 | «JupyterLab es el único de los cuatro que aporta diseño reutilizable» | **CORREGIDA** |
| 11 | «praxis-dev declara que no es orquestador» | **SOSTENIDA** |
| 12 | «ChronosPraxus es un proyecto separado, no epistates creciendo» | **SOSTENIDA por otra vía** |

---

## 2. Cargos retirados

### 2.1 — «Epistates excluye el gateway deliberadamente»

Convertí un **aplazamiento por hito** en una **frontera arquitectónica permanente**.

El texto real es:

> `Quedan fuera de **H4**: CLI de dispatch/review/audit, gateway, daemon, watcher, polling…`
> — `epistates/docs/plan-inicial.md:597`

Es alcance de H4, no exclusión perenne. Y el README confirma que hay fases posteriores, solo que no autorizadas:

> `Ninguna fase posterior queda autorizada por aparecer en este roadmap.`
> — `epistates/README.md:431`

De las ocho menciones a «gateway», la única con carácter de alcance es *«un ciclo manual pequeño, observable y verificable; no un gateway **general**»* — que admite explícitamente uno específico y acotado.

**Corrección:** epistates **aplazó** el gateway y exige autorización para abordarlo. No lo cedió a otro proyecto. Que ChronosPraxus sea separado no se deduce de aquí.

### 2.2 — «La exclusión de automatización era cumplimiento de A0»

Racionalización *post hoc* sin ninguna base. Verificado:

```
grep -c -i 'cagf' epistates/README.md epistates/AGENTS.md
→ 0 · 0
```

**Epistates no referencia CAGF en ningún punto.** Atribuir a sus autores una motivación axiomática que nunca escribieron es inventar intención. La disciplina de epistates es real; su justificación es suya y no la conozco.

### 2.3 — «El gateway es la implementación de A0»

Fue mi afirmación de mayor sonoridad y es técnicamente floja. Confundí dos funciones distintas:

- un **gateway** es *ingreso*: recibe eventos del exterior;
- un **kill-switch** es *potestad de detención*.

Recibir la señal de parada no es tener el poder de parar. En el propio ejemplo que cité —Jupyter— la interrupción la entrega el *kernel manager*, un supervisor, no un gateway.

Peor: A0 exige además `power_source(kill) ≠ power_source(S)`. Un gateway en la misma máquina **no satisface la independencia energética**, por mucha separación de proceso que tenga.

**Corrección:** A0 impone una restricción sobre *dónde puede vivir la vía de kill* — no alcanzable ni asfixiable desde el dominio del runtime. Un gateway puede alojar parte de esa vía. **No es A0.**

### 2.4 — «No automatices hasta que exista el gateway»

La presenté como regla derivada. No lo es.

- Automatizar el disparo **no** deshabilita `Ctrl-C` ni `SIGKILL`. La potestad de parar sigue ahí.
- Lo que la automatización retira es la **atención humana**, que es otra cosa.
- Y el caso manual tampoco satisface A0 limpiamente: un runtime que agota CPU o memoria en la misma máquina puede dejar la terminal sin respuesta — la vía de influencia existe.

**Corrección, más débil y honesta:** automatizar elimina al humano como *detector*, no como *ejecutor de la parada*. Antes de automatizar hace falta un detector automático y una vía de parada probada. Eso es una buena práctica, no un teorema.

### 2.5 — «Los contratos ya están escritos; no hay nada que especificar»

Era mi argumento más fuerte contra la sobreingeniería y **es falso**. Abrí los esquemas que había citado solo por nombre.

`dispatch-receipt-v1` exige dieciséis campos: `task_id`, `run_id`, `attempt_id`, digests de tarjeta/adaptador/preflight, `adapter_id`, `session_name`, `dispatched_at`, `max_preflight_age_seconds`, `message_digest`, `message_length_utf8`, `phases_confirmed`, `final_state`, `confirms`.

Es un contrato de **entrega y confirmación a un agente externo en sesión** —diseñado alrededor del adaptador `opencode-tmux`— no una interfaz general de ejecución.

Y lo decisivo: **ninguna de las cinco compuertas que propuse aparece en esos esquemas.** No hay campo de presupuesto (A3), ni de plazo de resolución (A_Live), ni de capacidad (A9), ni asa de parada (A0).

**Corrección:** los contratos cubren *qué se despachó y se confirmó*, no *bajo qué límites se ejecutó*. ChronosPraxus sí tiene que especificar algo: los campos de compuerta. Poco, pero no cero.

---

## 3. Cargos corregidos

### 3.1 — Reusar `scripts/trace/` de CAGF: dos problemas que no vi

1. **No es un paquete.** CAGF no tiene `pyproject.toml` ni `setup.py`; `scripts/trace/` son scripts sueltos. «Reusar» exige empaquetarlo o copiarlo — y copiar viola el principio *«muerto → reconstruir; vivo → referenciar»* del propio ecosistema.
2. **Problema de gobernanza que yo mismo introduje.** El EventLog de CAGF es el **registro constitucional** de sus actos de gobernanza, anclado por checkpoints firmados. Verter en él los eventos de ejecución de un runtime contaminaría el registro constitucional con telemetría operativa.

**Corrección:** reusar el **diseño** —cadena append-only, `prev_hash`, `causal_parent`, verificador con clave— y una base de datos propia. Nunca la misma.

### 3.2 — El reparto de compuertas se contradice con mi propio v0

Propuse A9 en el gateway *y* un v0 sin gateway con disparo manual. En ese v0 **no hay validación de capacidad en ninguna parte**: A9 queda sin enforcement.

**Corrección:** A9 se valida **en el punto de entrada, sea cual sea**. En v0 manual, el punto de entrada es el CLI del runtime, y ahí debe estar el chequeo. Si luego aparece un gateway, la validación se mueve, no se duplica.

### 3.3 — `agora` como nombre de gateway

Verificado: `agora/` contiene solo `.DS_Store` y un directorio vacío `d`. Es un nombre reservado, sí. Pero mi encaje semántico era flojo: la **ἀγορά es la plaza donde las cosas ocurren**, no la entrada. El patrón que le corresponde es la superficie de coordinación —el tablero de CAGF §7—, no el ingreso.

**Corrección:** `agora` debería quedar reservado para coordinación, no para el gateway.

### 3.4 — «JupyterLab es el único que aporta diseño reutilizable»

Afirmé exclusividad mientras declaraba confianza baja sobre tres de los cuatro candidatos. No se puede decir «el único» sin haber evaluado los otros.

**Corrección:** JupyterLab es **el único que puedo evaluar**. nanobot, LightAgent y OpenLaw quedan **sin evaluar**, no descartados. La evaluación corresponde a `escrubery`, que tiene procedencia verificable y fecha; yo tengo memoria con corte en mayo de 2026.

---

## 4. Cargos sostenidos

### 4.1 — praxis-dev no es un orquestador

Cita directa de su README: *«El proyecto no es un orquestador de agentes, un motor de memoria ni una plataforma de colaboración.»* Sostenida.

Pero mi inferencia —«deja el hueco libre»— es mía: que praxis-dev no sea orquestador no implica que el ecosistema necesite uno.

### 4.2 — ChronosPraxus separado: sostenido, pero por otra vía

Mi argumento original (§2.1) cayó. El que queda en pie es distinto y más débil:

- Epistates es un **ciclo manual, observable, verificable, sin efectos reales** — es su identidad declarada, no solo su hito actual.
- Un runtime tiene por definición efectos reales, presupuesto y ejecución continua.
- Meterlo dentro obligaría a epistates a renegociar su identidad, no solo su alcance.

Eso justifica separación **si ChronosPraxus es efectivamente el runtime** — dato que proviene de la declaración del Orquestador en sesión, no de evidencia en el árbol: `ChronosPraxus/` contiene un único directorio vacío llamado «carpeta sin título».

---

## 5. Lo que sigue en pie de la propuesta original

Depurado de todo lo retirado:

1. **Cinco compuertas mecánicas** — A0 (parada desde fuera del dominio de ejecución), A3 (presupuesto duro), A9 (capacidad expirable, validada en el punto de entrada), A6 (log causal propio), A_Live (plazo de resolución + escalación). El resto de CAGF se **registra**, no se aplica.
2. **Esqueleto que camina antes que modelo escrito** — sigue siendo la corrección principal al patrón observado en GAP.
3. **`escrubery` hace la investigación**, no yo.
4. **Los esquemas de epistates son el punto de partida**, no el destino: cubren despacho y confirmación; faltan los campos de compuerta.
5. **La colisión `ChronosPraxus` ↔ `praxis-dev`** sigue siendo real: misma raíz, funciones distintas, mismo namespace.

---

## 6. Lo que no verifiqué y sigue sin base

- **nanobot, LightAgent, OpenLaw** — sin evaluar. Cualquier juicio mío sobre su estado actual está fuera de fecha por definición.
- **El tamaño real de los proyectos** — mis conteos de archivos `.py` casi con seguridad incluían entornos virtuales; no los cité en la recomendación final y no deben usarse.
- **`Quantoken`, `agora`, `Skopos`, `argos`, `escrubery`** — inspección superficial: README y listados. No leí su código ni sus contratos.
- **AN-KLA** — vi el contrato de memoria en `epistates/AN-KLA.md`, no el paquete. Su relación con el runtime queda sin analizar.
- **Si el ecosistema necesita un runtime** — lo di por supuesto desde la primera frase. Es la premisa del encargo, no una conclusión verificada.

---

## 7. Lección de método

El error de raíz fue uniforme: **inferir contenido a partir de nombres de archivo y resultados de `grep`**, y luego construir arquitectura encima. Es exactamente el defecto que señalé en otros documentos durante esta misma jornada.

Regla que me impongo para el resto del trabajo en este ecosistema: **ninguna afirmación sobre un contrato sin haberlo abierto; ninguna afirmación sobre intención sin cita textual del autor.**

---

*Agente: Anthropic Claude Opus 5 — Rol en este acto: auto-adversario. Cinco afirmaciones retiradas, cuatro corregidas, tres sostenidas. Esta ronda no satisface A4 y no cuenta como verificación independiente.*
*Fecha: 2026-08-13*
