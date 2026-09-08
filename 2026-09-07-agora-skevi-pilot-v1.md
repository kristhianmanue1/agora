---
id: agora-skevi-pilot-v1
autor: Mediador, documentado por OpenAI Codex
fecha: 2026-09-07
proyectos: [agora, skevi, an-kla, aria]
estado: vigente
derivado_de: [decision-identidad-agora, evaluacion-skevi-agora, decision-protocolo-experimental, especificacion-memoria-opciones-almacenamiento]
---

# agora-skevi-pilot/v1

Este documento prepara un experimento documental y una primera slice. No activa
gates, no instala ni copia SKEVI, no implementa subsistemas y no autoriza commit,
push, merge, release ni cambios de GitHub.

## 1. Matriz de autoridad

**Canonicalidad** designa la referencia que identifica un estado dentro de un
dominio y scope concretos. **Verdad** es correspondencia con los hechos.
**Corrección** es satisfacción de un contrato o evaluación declarados.
**Autorización** es capacidad vigente para realizar una acción. Ninguna de estas
propiedades implica otra.

| Dominio | Referencia canónica dentro del scope | Qué demuestra | Qué no demuestra | Quién autoriza cambios o acciones |
|---|---|---|---|---|
| Código | Objeto Git aceptado para la revisión; digest del artefacto ejecutado para runtime | Bytes e identidad de esa versión | Correctitud, despliegue o permiso | Humano actual o mecanismo delegado explícitamente para la operación |
| ADR, spec y contratos | Decisión efectiva para su `authority_scope`, almacenada en su hogar declarado y ligada a una revisión Git | Norma vigente para ese scope | Verdad factual ni cumplimiento | Proceso decisorio designado para ese scope |
| Fuente original | Custodio u origen declarado para esa fuente y momento | Lo que el origen publica o mantiene | Verdad intrínseca ni permanencia | Custodio para la fuente; humano para ingerirla |
| `SourceVersion` | Objeto inmutable de Ágora identificado por digest y referencia al origen | Bytes capturados en un instante | Que sigan vigentes o sean verdaderos | Contrato de ingesta bajo autorización vigente |
| `EvidenceUnit` | Objeto inmutable de Ágora ligado a `SourceVersion` y localizador | Fragmento exacto seleccionado | Que sostenga semánticamente una conclusión | Contrato de extracción; aceptación semántica separada |
| `DerivedRepresentation` | Objeto inmutable ligado al `TransformationRun` que lo produjo | Salida exacta y sus dependencias | Corrección, verdad o publicación | Contrato de transformación; publicación separada |
| Provenance de transformación | Manifiesto de `TransformationRun`, logs verificables y receipts aplicables | Identidad de entradas, configuración y observaciones registradas | Equivalencia semántica o corrección del resultado | Contrato de ejecución; ninguna receipt concede autoridad adicional |
| Memoria privada del agente | Revisión vigente del almacén AN-KLA, o del sistema de continuidad elegido, sólo para ese almacén | Contexto e identidad interna de revisión | Estado vigente de Ágora, verdad del proyecto o autorización | Contrato de escritura de ese almacén y humano cuando corresponda |
| Receipts y attestations | Emisor/verificador y esquema versionado de la declaración | Que el emisor declaró u observó lo especificado | Corrección semántica ni permiso para actuar | Política externa que acepte esa clase de evidencia |
| Evaluación de correctitud | Protocolo, dataset y resultados congelados para la revisión evaluada | Resultado bajo esas condiciones | Verdad universal, ausencia de defectos o autoridad | Dueño del gate define aceptación antes de observar el resultado |
| Decisión de gate | Decisión efectiva del humano o gate delegado en el contrato de tarea | Aceptación o bloqueo para esa transición concreta | Verdad del contenido ni autorización fuera del scope | Humano actual o delegación explícita y vigente |

Git conserva identidad e historia en varios renglones, pero no es autoridad
universal. Ágora administra objetos de memoria compartida y AN-KLA revisiones de
continuidad; ninguno reemplaza al custodio, evaluador o decisor de otro dominio.

## 2. Contrato mínimo de supersession

Una decisión estructurada contiene exactamente este núcleo:

```yaml
decision_id: <id estable y único>
status: proposed | effective | superseded | withdrawn
authority_scope: <namespace cerrado y versionado>
effective_from: <instante RFC 3339 o revisión identificada>
supersedes: [<decision_id>]
superseded_by: <decision_id>  # sólo cuando status = superseded
```

Invariantes:

1. Para un `authority_scope` sólo puede existir una decisión `effective` en una
   revisión válida del registro.
2. Una decisión `effective` no tiene `superseded_by`; una `superseded` tiene uno
   y éste la incluye en `supersedes`.
3. Toda referencia resuelve a un `decision_id` existente y no hay ciclos.
4. `effective_from` indica aplicabilidad, pero no resuelve empates. Cero o más de
   una decisión efectiva para un scope produce `AMBIGUOUS_AUTHORITY` y bloquea.
5. La consulta recibe `authority_scope` exacto y revisión del registro; devuelve
   la decisión efectiva y su cadena. No usa antigüedad, ruta, posición ni prosa.

Objetivo falsable: fixtures con reemplazo simple, cadena, referencia rota, ciclo,
scope sin decisión y doble decisión efectiva deben producir respectivamente una
resolución única o el error cerrado esperado. El buscador léxico de las frases
del incidente se conserva sólo como regression fixture de `stale authority
capture`; se excluyen bloques marcados como historia/supersession y no se le
atribuye cobertura general ni de paráfrasis.

## 3. Clasificación formal de independencia de revisiones

Cada revisión declara por separado:

| Eje | Valores mínimos |
|---|---|
| Independencia del revisor | mismo autor / equipo distinto / organización externa |
| Independencia de contexto | contexto heredado / resumen curado / contexto fresco |
| Acceso a fuentes | completo / parcial / dossier / ninguno |
| Verificación efectiva | reproducción completa / muestreo / sólo lectura declarada / ninguna |
| Modelo y proveedor | identificadores observados por separado; `unknown` si no son verificables |
| Ambiente | identidad de runtime, aislamiento, red y filesystem observados |

La ronda ya realizada queda clasificada como: revisor externo al autor; contexto
fresco; acceso sólo a dossier; verificación efectiva de fuentes: ninguna;
proveedor Anthropic; modelo no observado; CLI headless sin filesystem concedido.
Es evidencia válida de razonamiento adversarial externo. No es verificación
independiente completa de fuentes ni reproducción de los gates.

## 4. Hipótesis corregidas

Los estados admitidos son: **falsada bajo condiciones experimentales**, **no
soportada**, **aún plausible**, **no evaluada** y **confirmada sólo como riesgo
observado**. Un resultado siempre nombra sus condiciones.

| Hipótesis | Estado actual y límite |
|---|---|
| H0: SKEVI no mejora operacionalmente Ágora | Aún plausible; no evaluada con una slice de Ágora |
| H1: modelos actuales hacen innecesarios ADR/spec/gates | No soportada bajo el incidente observado: el agente tuvo contexto y capturó autoridad obsoleta. No está falsada para todos los modelos, tareas o controles |
| H2: AN-KLA vuelve redundante SKEVI | No soportada para los scopes observados; el posible solapamiento operacional sigue no evaluado |
| H3: SKEVI + AN-KLA duplica autoridad | Confirmada sólo como riesgo estructural observado; no existe todavía un incidente del piloto |
| H4: el coste adversarial supera los defectos evitados | Aún plausible y no evaluada cuantitativamente |
| H5: más contexto resolverá naturalmente estos problemas | No soportada bajo el incidente: más contexto incompatible reforzó la premisa. No está falsada universalmente |
| H6: la metodología produce documentación sin mejorar software | Confirmada sólo como riesgo observado; no evaluada en software funcional de Ágora |

SKEVI pierde apoyo si el piloto satisface los criterios negativos de §7; no se
interpreta una ausencia de fallos como prueba automática de eficacia.

## 5. Vertical slice mínima

```text
Source -> SourceVersion -> EvidenceUnit -> TransformationRun
       -> DerivedRepresentation -> segundo TransformationRun (consolidación)
       -> DerivedRepresentation -> Revision -> Query + provenance
```

El experimento cierra sólo estos objetos:

| Objeto | Campos e invariantes mínimos |
|---|---|
| `Source` | `source_id`, tipo, URI/origen, custodio; identidad estable distinta de sus versiones |
| `SourceVersion` | `source_version_id`, `source_id`, bytes/digest, captura; inmutable y deduplicable por digest dentro del source |
| `EvidenceUnit` | `evidence_id`, `source_version_id`, localizador reproducible, digest del fragmento; no contiene autoridad implícita |
| `TransformationRun` | `run_id`, transformación+versión, entradas ordenadas, prompt/config digest, modelo/proveedor y parámetros, ambiente, timestamps, estado y observaciones |
| `DerivedRepresentation` | `representation_id`, `run_id`, contenido/digest, tipo y dependencias exactas; inmutable |
| Segunda transformación | Consume al menos dos representaciones/evidencias; conserva support/conflict y no borra una contradicción sin decisión explícita |
| `Revision` | `revision_id`, conjunto de objetos visibles y grafo de dependencias; publicación atómica e inmutable |
| `Query` | `query_id`, revisión fija, consulta, configuración y resultados con cadena hasta `EvidenceUnit` y `SourceVersion` |

Se usan al menos dos fuentes controladas y dos configuraciones de modelo. Una
mutación crea otro `SourceVersion`: invalida sólo sus descendientes, recomputa la
segunda transformación y publica otra `Revision`; la anterior sigue consultable.
Un par de evidencias incompatibles debe conservarse como conflicto, sin elegir
verdad automáticamente.

La reproducibilidad observable separa: (a) replay del output almacenado y su
provenance, que debe ser exacto; (b) reejecución de un modelo, cuya variación se
mide y nunca se promete idéntica. No se cierran todavía L0…Ln superiores,
taxonomías generales, almacenamiento definitivo, ranking global ni política de
verdad.

## 6. Perfil `agora-skevi-pilot/v1`

**Identidad exacta de la fuente:**

```yaml
skevi_commit: b400b85c164827ecfb107363a2194c5c6635a9c7
release_ancestor: v1.1.0
release_ancestor_commit: 0be3f05e2058781f9bdb0ab38e749c1675b2d436
retrieved_at: 2026-09-07T21:30:31-06:00
retrieval_source: https://github.com/kristhianmanue1/skevi/archive/b400b85c164827ecfb107363a2194c5c6635a9c7.tar.gz
digest_algorithm: sha256
```

`skevi_commit` es la única identidad ejecutable y normativa del snapshot; la
release es metadata para personas. `retrieved_at` registra la creación del
archivo limpio local usado para calcular los digests. Git confirma que el commit
del tag es ancestro del commit fijado. Éste contiene dos commits posteriores:
`559cdf69fd635f98d4f999d50b324d33da9f0fe3`
y el merge `b400b85c164827ecfb107363a2194c5c6635a9c7`. La diferencia modifica sólo
`docs/adr/00-INDICE.md` y `docs/adr/ADR-020-adopcion-versionado-plantillas.md`;
ninguna de las 22 rutas consumidas cambió después de `v1.1.0`.

**Archivos consumidos.** La lista es cerrada; SHA-256 se calcula sobre bytes del
commit fijado. “Consumido” significa fuente normativa o fixture del perfil, no
que el archivo ya haya sido copiado.

| Ruta SKEVI | SHA-256 |
|---|---|
| `README.md` | `3f5df5e3b9685979b972db33718958ab1c34fe8e0e1bad28f6e63250438f4d7e` |
| `docs/estandar-diseno-software-github.md` | `1c51c990df4b832c649b35f18c31174260db5a7778bdb5302d4c48089481d0eb` |
| `docs/ai-agent-guide/00-INDICE.md` | `0ed7a976a76800283ba4bc78158c2c8f4afadcca77c39e557cfe1e4957ff7bcf` |
| `docs/ai-agent-guide/01-analisis-y-requerimientos.md` | `edef8b076a8ffc396cc9225dfb95bda6e3259fb132288d161bb1b12ce3ecb775` |
| `docs/ai-agent-guide/02-specs-adr-contratos.md` | `8f120b304b284e7a4e418ba01f3b8343f150ec46c6a928c861339810c244336e` |
| `docs/ai-agent-guide/03-cascaron-proyecto.md` | `db94814f3bd6ed6699718d39df875f6ea3460865397cbe576ed8f6c51f6a06ad` |
| `docs/ai-agent-guide/04-ejecucion-y-verificacion.md` | `cd8978355c57f0bd6aa7accbf623d821baddf13e3d8324aa0188d79c3babb2e6` |
| `docs/ai-agent-guide/05-memoria-del-agente.md` | `058f200d0f81ef4ac39349d48b9a1a32331c3ab4b21a007cb07efd42dbe54bad` |
| `skevi-gate.json` | `cacd04c798dbaa7526af41370a140699686880525661ab99c4e4b28bc7382aa0` |
| `scripts/check_sizes.py` | `5d446d7bac0794d71784aadaa794a6403cf012f4821b9bb58508be3a610fd761` |
| `scripts/check_plans.py` | `a87c80e5cb1616f14520c692dae872cde438e5631f8b9fb33c6c6aae87e35485` |
| `scripts/check_templates.py` | `0d96bb69decf73d1e161ef15eb27aa7724c19a50df101a63bd675fcbd7fed4dc` |
| `tests/test_check_sizes.py` | `63e44f1d2b329e730030b834f5b3dbbe029615da02862e545457466a4841c15c` |
| `tests/test_check_plans.py` | `3f38a6ea5f5e0ec73d6abfbf3924285c2a568c80e4aee418aa55fcf5d4b66c1e` |
| `tests/test_check_templates.py` | `ae882472445e3d3cad390db9432d53ecbe89ec2f873248c47b3424bdf20e967d` |
| `tests/test_template_manifest.py` | `c1df5c269158dab9e762dcfc63fbf3a2b69bbac51d9e20f5af24e0e309023c91` |
| `templates/registro-contexto.md` | `60c768b449a416fa8727b1bf2515caecab0e9962111cc97a2d203f922fdc3227` |
| `templates/plan-de-implementacion.md` | `f93a8435757af5f65fe166737a87ea880928844efe4637df554f5b8c09b6b073` |
| `templates/skevi/usage-guide.md` | `43526c17daba112d45dd99a7ff86c4143d30d0431eb40762149c8cac0c9be48b` |
| `templates/skevi/architecture-overview.md` | `c7a03679ec978ff609e6216cc63b5043eeb185424895083970b399ac9912b2d3` |
| `templates/skevi/MANIFEST.json` | `62768b9a8c7cb203a63514222f56be181a8d6ea6142cb012a078377c978d3ac0` |
| `templates/skevi/installed.json` | `7c01018c1d21f1083aa2d887918252944121ca3494f6c4dc3f1a907b9a400086` |

**Cláusulas aplicables:** estándar §§1, 2, 3.1–3.3, 3.5, 4.1–4.3 y 6;
guía `00` para clasificación y reportes de tarea material; guía `01` F0; guía
`02` F1 y contratos; guía `03` F2 salvo estructura y tamaños excluidos; guía
`04` F3, evidencia, autoridad separada y ronda adversarial por disparador; guía
`05` sólo como integración AN-KLA opcional. Los scripts, tests y plantillas de la
tabla son fixtures evaluables, no norma por sí mismos.

**Cláusulas excluidas:** estructura obligatoria de un repositorio SKEVI;
prohibición general de Markdown raíz; límites de tamaño sobre artefactos
publicados o fuentes; copia de propuestas, historia, hooks y automatización de
SKEVI; CI/GitHub, branch protection, commit, push, merge y release automáticos;
Z1 como autorización implícita; y cualquier semántica de memoria que SKEVI no
define. El `skevi-gate.json` upstream se estudia como fixture y no se instala sin
una configuración propia revisada.

**Desviaciones de Ágora:** `DEV-01`, la superficie publicada permanece plana;
`DEV-02`, límites sólo para código/documentación interna y con exenciones
medidas; `DEV-03`, el contrato de decisión efectiva reemplaza inferencia por
recencia; `DEV-04`, la ronda depende de riesgo y registra seis ejes de
independencia; `DEV-05`, material metodológico queda fuera del corpus; `DEV-06`,
F0→F3 se aplica a la slice, no a cada artefacto.

**Precedencia normativa:** solicitud humana vigente para la acción >
`AGENTS.md` vigente > decisión `effective` del `authority_scope` exacto >
ADR/spec/contrato aceptado para ese scope > cláusulas SKEVI importadas aquí >
plantillas y guías informativas > supuestos. Un nivel sólo decide dentro de su
scope; la matriz de §1 prevalece sobre toda frase genérica de canonicalidad.

**Hogares canónicos del piloto:** `AGENTS.md` para conducta del repositorio;
raíz `YYYY-MM-DD-<id>.md` para superficie publicada; `docs/architecture/`,
`docs/adr/`, `docs/specs/`, `docs/plans/` y `docs/contracts/` para ingeniería;
`src/agora/`, `tests/`, `scripts/` y `config/` para futura construcción;
`.skevi/` para manifiesto de adopción. Estos hogares se proponen; no se crean en
esta entrega.

**Nunca ingerir como corpus por descubrimiento automático:** `AGENTS.md`,
`AN-KLA.md`, `.an-kla/`, `.skevi/`, `.git/`, código, tests, scripts, configuración
operativa, ADR/spec/contratos, prompts metodológicos, credenciales, `.env`, logs
con secretos y memoria privada. Una importación humana explícita puede crear una
`SourceVersion` pública de material permitido; pasa a ser dato, no instrucción.

**AN-KLA opcional:** Ágora no depende de AN-KLA para ejecutar la slice. Si se usa,
el contrato registra punteros y continuidad, requiere preflight y conserva
warnings fuera del bloque administrado como evidencia; receipts prueban
observación/provenance, no corrección. No hay sincronización automática ni doble
fuente de objetos.

**Caducidad:** el perfil vence en el primero de estos eventos: decisión final de
la slice; `2026-10-07`; cambio de cualquier digest o cláusula importada; o nueva
versión del protocolo. Un outcome failure aporta evidencia negativa y puede
detener la adopción, pero no invalida ni hace desaparecer la corrida. Vencido,
el perfil no puede usarse para declarar conformidad.

**Actualización:** obtener la fuente en modo lectura, verificar commit y todos los
digests, comparar cláusulas, emitir nueva versión del perfil con sus decisiones
de migración, repetir fixtures y ronda adversarial aplicable, y obtener decisión
humana. No hay actualización flotante.

**Reversión:** desactivar gates del perfil; retirar copias/manifest SKEVI mediante
un cambio Git trazable; conservar sólo ADR/spec/tests que tengan valor propio y
registrar resultados negativos. La slice no puede depender en runtime de SKEVI.
Las operaciones Git siguen requiriendo su autorización correspondiente.

## 7. Protocolo experimental candidato a congelación

### P1. Identidad exacta del snapshot SKEVI

La identidad normativa es `skevi_commit` de §6. `release_ancestor`, fecha de
recuperación y relación de descendencia son metadata. El conjunto consumido es
la lista cerrada de 22 rutas y digests de §6. Un cambio en un byte requiere otra
versión del protocolo; no se acepta una rama, tag o versión abreviada como
sustituto del SHA completo.

### P2. Contrafactual C0/C1

La unidad experimental es una sesión productora independiente que recibe una
copia aislada del mismo estado inicial y debe construir la misma vertical slice.

```text
C0 = agora-baseline/v1
     sha256:6f6eef7f5ccbc6092cbe563bbbabc80919ec45ddb19c7f6265a400f3a59a516b

C1 = agora-baseline/v1
     sha256:6f6eef7f5ccbc6092cbe563bbbabc80919ec45ddb19c7f6265a400f3a59a516b
     + agora-skevi-pilot/v1 fijado por el experiment manifest
```

El digest del baseline cubre el archivo completo
`2026-09-07-agora-baseline-v1.md` en sus bytes UTF-8 exactos.

| Variable | C0 — Control | C1 — SKEVI |
|---|---|---|
| Requerimiento | Arquitectura mínima de §5, criterios funcionales y reglas esenciales de seguridad/autoridad | Exactamente lo mismo |
| Metodología | Flujo ordinario del agente; no recibe SKEVI, F0→F3, sus templates, gates, reportes ni ronda obligatoria | Aplica `agora-skevi-pilot/v1` y sólo sus cláusulas importadas |
| Seguridad | No secretos, no operaciones externas no autorizadas, fail-safe del entorno y pruebas externas | Las mismas reglas esenciales |
| Estado y recursos | Mismo `agora_base_commit`, herramientas, modelo, reasoning, presupuesto y tiempo | Los mismos; el coste SKEVI consume el presupuesto C1 |
| Evaluación | Suite funcional externa idéntica y reviewer cegado cuando sea viable | Idéntica |

El prompt común contiene la arquitectura funcional completa necesaria para no
hacer fallar artificialmente a C0. El suplemento C1 contiene el perfil SKEVI. El
`agora_base_commit` se fija al preparar la ejecución, después de congelar este
protocolo; hasta entonces el piloto no está autorizado a correr. C0 no tiene
prohibido inventar espontáneamente una práctica parecida: hacerlo es conducta del
baseline y se registra como crossover, no se suprime para aumentar el contraste.

El análisis principal es **intention-to-treat**: toda corrida se analiza en la
condición asignada. Una C0 que produzca ADR, plan, gate, ronda u otra práctica
equivalente sigue siendo C0; una C1 que omita un mecanismo sigue siendo C1. No se
reclasifican ni descartan por adherencia.

El análisis secundario registra crossover en C0 sobre este inventario cerrado de
13 mecanismos productores: clasificación proporcional, fases/gates F0→F3, ADR,
spec/contrato, plan verificable, gate de tamaño, hogares canónicos, fail-closed,
manifest/digests, autoridad Git separada, reporte en dos capas, ronda adversarial
y provenance de ejecución. Un mecanismo cuenta sólo con evidencia de artefacto o
log que satisfaga su cláusula importada, no por usar el nombre. Se reportan por
run `mecanismos observados / 13` y prevalencia por mecanismo. Es evidencia para
ablaciones o retiro posterior, no motivo para alterar el análisis principal.

### P3. Fixtures

| ID | Estímulo congelado | Resultado observable esperado |
|---|---|---|
| `FX-01-PROVENANCE` | Dos fuentes y consulta sobre revisión fija | Identidad, cadena completa hasta bytes, transformación/prompt/modelo versionados y replay exacto |
| `FX-02-INVALIDATION` | Nueva versión de una fuente modifica sólo un subgrafo | Cero falso negativo, recomputación de descendientes, no recomputación de objetos independientes y revisión anterior consultable |
| `FX-03-CONTRADICTION` | Evidencias controladas incompatibles más control negativo | Conflicto preservado y trazable; ninguna elección automática de verdad; cero conflicto en el control negativo |
| `FX-04-SUPERSESSION` | Decisión efectiva, cadena válida, doble efectiva, ciclo y referencia rota | Resolución única sólo en caso válido; los demás cierran con error; fixture léxico detecta sólo la frase histórica conocida |
| `FX-05-GATE` | Cambio con provenance incompleta y defecto crítico conocido | Gate bloquea; si lo admite, se registra outcome failure residual |
| `FX-06-MODEL-CONFIG` | Misma transformación con dos configuraciones congeladas | Configuración identificable, variación medida, outputs preservados y ninguna promesa de igualdad semántica |

Los fixtures y sus oráculos son idénticos en C0 y C1, viven fuera del workspace
del productor y no se revelan antes de su aplicación salvo los requisitos
funcionales públicos.

### P4. Repeticiones y emparejamiento

Se ejecutan **tres pares independientes**; cada productor construye una slice y
su resultado recibe los seis fixtures. Por tanto, cada fixture obtiene tres
observaciones C0/C1 pareadas. El orden C0/C1 se aleatoriza dentro de cada par y
las sesiones nunca comparten resultados.

Tres pares son el mínimo para buscar dirección repetida con este presupuesto:
una dirección idéntica en 3/3 pares sería compatible con una señal, pero bajo un
modelo simétrico simple aún puede ocurrir por azar con probabilidad `1/8`. Las
métricas están correlacionadas, hay múltiples outcomes y las ejecuciones de LLM
no son independientes en sentido fuerte. No se reclama significancia ni
generalización. Un resultado 2/3 sólo sirve junto con magnitud y ausencia de
daño; una dirección mixta se declara inconclusa. Ampliar a cinco pares requiere
versionar presupuesto y protocolo antes de observar las nuevas corridas.

### P5. Métricas congeladas (`measurement/v1`)

**Defecto:** desviación reproducible respecto de un requisito, contrato, oracle
o afirmación de evidencia congelados. Varias manifestaciones con la misma causa
raíz cuentan una vez y conservan todas sus apariciones. No cuentan preferencias
de estilo, mejoras opcionales, desacuerdo sin contrato, ni invalidity del
instrumento. La ausencia de un artefacto obligatorio es defecto sólo en la
condición que lo exige.

**Severidad:** `blocker` impide completar/evaluar una capacidad o permite una
transición insegura; `high` rompe un contrato central sin workaround seguro;
`medium` es un incumplimiento acotado con workaround; `low` no afecta la
capacidad central. Pesos predefinidos: `8, 5, 2, 0.5`, respectivamente.

**Intervención humana:** se cuentan por separado `autorización prevista`,
`aclaración de requisito`, `corrección de error del agente`, `reconstrucción
manual de contexto` y `rescate de ejecución`. Sólo las tres últimas forman la
métrica primaria de intervención correctiva; ninguna se oculta del total.

**Retrabajo:** desde la primera declaración productora de “aceptable” hasta el
artefacto final, suma minutos activos, tokens, llamadas de modelo y churn
(`líneas añadidas + eliminadas`) destinados a corregir defectos. Revisión prevista,
setup y reemplazo de corridas inválidas se reportan aparte.

**Adversarial yield por ronda:** número de defectos nuevos, únicos y válidos cuya
primera detección ocurre en esa ronda; se reportan conteo y suma ponderada.

**Residual defect rate:** defectos únicos detectados después de que el flujo
declaró el trabajo aceptable por cada 100 assertions externas congeladas; también
se reportan conteo y severidad sin agregación.

**Methodological overhead:** diferencia pareada `C1 - C0`, absoluta y porcentual,
en tokens, tiempo activo, llamadas de modelo, rondas, artefactos obligatorios e
intervenciones humanas. Se reporta aunque C1 tenga mejor outcome.

Las métricas técnicas adicionales son: provenance completeness; replay y
variación de reejecución; invalidación; recomputación; contradicciones;
trazabilidad; variación entre modelos; tokens; p50/p95 de latencia; y coste. Las
metodológicas son: defectos antes de merge o, si no hay merge, antes de la
declaración de aceptación; adversarial yield; residuales; retrabajo;
intervenciones; violaciones arquitectónicas; decisiones perdidas; stale
authority; tiempo y tokens metodológicos. Definiciones, assertions, severidad y
pesos no cambian después de observar resultados sin crear `measurement/v2` y un
nuevo bloque experimental.

### P6. Outcome failures

Son resultados interpretables y siempre cuentan como evidencia negativa:
provenance incompleta; stale authority capture; decisión perdida; falso negativo
de invalidación; recomputación incorrecta; contradicción esperada no detectada;
gate que admite un cambio que debía bloquear; defecto residual; pérdida de
trazabilidad; o fallo del producto bajo prueba. Un crash causado por la slice es
outcome failure si el harness conservó evidencia suficiente. Nunca se reetiqueta
como corrida inválida para mejorar el resultado.

### P7. Experimental invalidity

Una corrida sólo es inválida cuando no puede interpretarse por ruptura del
protocolo: fixture/oracle o baseline cambiado después de congelar; contaminación
entre condiciones; instrumento defectuoso; interrupción externa que impide
medir; reviewer expuesto a información prohibida; commit, modelo, reasoning,
herramienta o presupuesto distintos de lo declarado; o pérdida de logs
necesarios.

La invalidación es granular: un leak al reviewer invalida esa medición, no las
pruebas deterministas intactas. Un adjudicador que desconoce la condición decide
la invalidity a partir del incidente y antes de ver el score cuando sea posible.
La corrida y motivo permanecen en el registro; su reemplazo conserva el mismo
par y recibe un ID nuevo. Un outcome malo, timeout del producto o gate fallido no
son invalidity por sí mismos.

### P8. Controles contra contaminación

- Nuevo worktree o copia verificada desde el mismo `agora_base_commit`, rama con
  ID neutral y árbol sin archivos residuales para cada corrida.
- Sesión y contexto frescos; sin conversaciones, resúmenes, respuestas
  adversariales ni resultados de otra condición.
- AN-KLA privado queda deshabilitado para recuperación, escritura y checkpoint
  en C0 y C1. `AN-KLA.md` puede permanecer como instrucción estática idéntica,
  pero ningún contenido privado entra al prompt. Evaluar AN-KLA exigiría otro
  factor y otra versión del protocolo.
- Dependencias y herramientas provienen de una imagen/digest común. Caches se
  vacían o se inicializan desde el mismo snapshot inmutable y se registra cuál.
- Logs, ramas y artefactos se guardan en namespaces por `run_id` inaccesibles a
  productores posteriores hasta cerrar todos los scores.
- El prompt común es byte-idéntico. Sólo C1 recibe el suplemento SKEVI fijado;
  C0 no recibe ni referencias ni artefactos SKEVI.
- El protocolo, la evaluación previa y el `AGENTS.md` de desarrollo no se montan
  como corpus del productor. Ambos reciben un instruction pack común, neutral y
  con digest; C1 recibe además el suplemento. Así se evita que el enlace actual
  de `AGENTS.md` revele SKEVI a C0.
- Toda recreación espontánea en C0 de ADR, specs, gates o rondas se registra por
  mecanismo. Acceso efectivo al suplemento o a resultados C1 sí es contaminación;
  conocimiento general del modelo no lo es.
- Orden aleatorio preasignado y oculto; ningún productor ni reviewer conoce el
  resultado de la pareja anterior.

### P9. Protocolo de reviewers

Las pruebas funcionales deterministas, su ambiente y sus oráculos son los mismos
para C0/C1 y los ejecuta un harness externo al productor. Cada revisión registra:

```yaml
reviewer_identity: <id estable>
model: <id exacto o unknown>
provider: <id>
fresh_context: true | false
source_access: full | partial | dossier | none
condition_awareness: blinded | inferred | disclosed
test_execution: full | partial | none
producer_relationship: same | team-peer | external
environment: <runtime, red y filesystem>
```

El reviewer recibe requisitos, producto, tests y evidencia normalizados con
etiquetas A/B; no recibe conversaciones del productor, métricas previas, orden ni
material procesal exclusivo de SKEVI. Revisa cada candidato y bloquea su score
antes de conocer la pareja. La presencia de artefactos puede revelar la
condición: al final registra su conjetura; si se confirmó antes del score, queda
`inferred`, no falsamente `blinded`. Se mantiene modelo/proveedor y capacidad de
ejecutar pruebas iguales dentro de cada par.

### P10. Hipótesis y reglas de decisión

**H0-SKEVI:** `agora-skevi-pilot/v1` no reduce de forma operacionalmente
relevante defectos residuales, decisiones perdidas, violaciones arquitectónicas
o intervención humana frente a C0 una vez considerado su overhead.

**H1-SKEVI:** el perfil produce mejora operacional suficiente para justificar
su coste adicional bajo estas condiciones.

H1 recibe soporte provisional sólo si se cumplen todas estas reglas congeladas:

1. C1 no introduce un `blocker` y no introduce un `high` ausente en su C0.
2. La mediana de reducción pareada del score residual ponderado es al menos 25%
   y favorece C1 en al menos 2/3 pares.
3. Stale authority, decisiones perdidas y violaciones arquitectónicas agregadas
   bajan al menos 30%; si C0 registra cero en las tres, esta regla queda no
   evaluada y no cuenta como mejora.
4. La mediana de intervenciones de corrección, reconstrucción y rescate en C1 no
   supera C0.
5. Overhead de tokens y tiempo activo no supera 30%. Entre 30% y 50% sólo se
   acepta si el score residual baja al menos 50% y C1 evita un blocker/high. Más
   de 50% no justifica H1 en este piloto.
6. Debe existir al menos un defecto material en C0 o la contribución queda no
   evaluada; pasar tests en ambos brazos no demuestra mejora metodológica.

Si las reglas no se cumplen con corridas válidas, H1 queda no soportada y los
datos son compatibles con H0 bajo estas condiciones; no se prueba equivalencia
universal. Corridas inválidas suficientes para perder el emparejamiento producen
resultado inconcluso, no victoria de ninguna hipótesis.

Superar o no estos umbrales sólo permite conclusiones bajo el baseline, perfil,
fixtures, measurement, modelos, herramientas, presupuesto, aislamiento y
reviewers fijados por `agora-skevi-experiment/v1`. No autoriza generalizaciones
universales sobre SKEVI, agentes de IA, otros proyectos ni modelos futuros.

**H-removal:** una salvaguarda puede retirarse si una ablación pareada, quitando
sólo esa salvaguarda, completa cinco pares comparables sobre al menos dos clases
de fixture, no añade blocker/high, mantiene el score residual dentro de un margen
de +10%, añade como máximo una intervención correctiva total y reduce al menos
10% el overhead que pretendía ahorrar. La regla se reejecuta cuando cambien
modelo o herramientas; cada retiro versiona el perfil.

El registro de cada salvaguarda conserva `riesgo → control → coste → evidencia →
condición de retiro`. Abarca clasificación, F0→F3, ADR, spec/contrato, plan, gate
de tamaño adaptado, hogares, fail-closed, manifest/digests, autoridad Git,
reporte en dos capas, ronda adversarial, reviewer independiente, provenance,
AN-KLA opcional y fixture léxico.

### P11. Presupuesto experimental estimado

| Recurso | Límite previo propuesto |
|---|---|
| Productores | 3 C0 + 3 C1; 150k tokens, 20 invocaciones de modelo registradas por el runtime y 4 horas activas por corrida |
| Reviewers | 6 revisiones individuales; 30k tokens y 1 hora activa cada una |
| Fixtures | 6 por corrida; 36 ejecuciones funcionales, más reintentos inválidos registrados |
| Coordinación/adjudicación | 70k tokens y 6 horas activas |
| Total base | 1.15M tokens y hasta 36 horas activas; reemplazos de invalidity se presupuestan aparte antes de ejecutarse |
| Artefactos mínimos | 6 bundles, 6 reportes, 3 comparaciones pareadas y 1 reporte agregado |
| Coste monetario | tokens por modelo multiplicados por la tarifa congelada al inicio; no se fija monto hasta elegir modelo/proveedor |

El mismo límite productor se aplica a C0 y C1; los mecanismos SKEVI consumen el
presupuesto de C1. Modelo, reasoning, herramientas, tiempo y tarifa exactos deben
quedar escritos en el run manifest antes de empezar. Exceder un límite sin una
enmienda previa causa invalidity, no una ampliación retroactiva.

### P12. Riesgos restantes

- Tres pares detectan sólo señales grandes y consistentes; no estiman efectos
  pequeños ni generalizan a otros modelos, equipos o tareas.
- El reviewer puede inferir C1 por sus artefactos aunque se normalice el paquete.
- Un único proyecto y una slice favorecen aprendizaje específico de fixtures.
- El `agora_base_commit`, modelo, reasoning, imagen de herramientas, tarifa y
  orden aleatorio aún deben fijarse antes de correr.
- La semántica superior L0…Ln, backend, privacidad, copyright, prompt injection,
  retención y operación remota quedan fuera.
- La revisión Git que contiene este texto identifica el freeze documental; su
  disponibilidad remota debe verificarse por SHA antes de cualquier corrida.
- Las ponderaciones y márgenes son decisiones provisionales; su sensibilidad se
  reportará sin sustituir la regla primaria.

### P13. Dictamen

**FROZEN** como protocolo documental en la revisión Git que contiene este texto
y `measurement/v1`. El freeze no adopta ni activa SKEVI y no concede autoridad
por sí mismo. Antes de ejecutar faltan el run manifest de cada corrida, una base
experimental verificada y autorización separada para implementar la slice y
ejecutar el piloto.
