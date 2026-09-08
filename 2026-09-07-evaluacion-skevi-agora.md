---
id: evaluacion-skevi-agora
autor: OpenAI Codex
fecha: 2026-09-07
proyectos: [agora, skevi, an-kla, aria]
estado: vigente
derivado_de: [proposal, decision-identidad-agora, decision-protocolo-experimental, especificacion-memoria-opciones-almacenamiento]
---

# Evaluación crítica de Skevi para Ágora

Evaluación de arquitectura y metodología; no autoriza copiar Skevi, construir
subsistemas de Ágora, instalar dependencias, cambiar GitHub, commit ni push.

## Evidencia y alcance

- Los siete Markdown presentes antes de este informe se revisaron completos en
  el árbol de trabajo.
- Skevi publicado evaluado en `b400b85`, separado de un checkout local con
  cambios ajenos sin commit: `check_sizes` OK sobre 95 archivos, `check_plans`
  OK sobre 2 planes y 110 tests OK.
- Release publicada: `v1.1.0`; el tag resuelve al commit `0be3f05` y `main` tiene
  dos correcciones documentales posteriores hasta `b400b85`.
- Ágora no tiene workflows, rulesets ni protección de `main` observados.
- La evaluación no demuestra que Skevi mejore todavía la construcción de Ágora.

## Aplicabilidad

### A. Aplicación directa

- Clasificación proporcional Spike/Bounded/Architectural para no usar el mismo
  proceso en una consulta, un cambio acotado y una frontera nueva.
- F0→F3 para el motor: requisitos falsables, contratos, cascarón, implementación
  y verificación.
- ADR para almacenamiento, semántica L0…Ln, revisiones, configuración de modelos,
  consolidación, invalidación y contratos de integración.
- Specs y contratos cerrados para fuente, evidencia, transformación, revisión,
  consulta, publicación y CLI.
- Planes verificables sólo cuando el trabajo requiera varias tareas dependientes.
- Fail-closed, evidencia ejecutable y rondas adversariales para persistencia,
  salidas de LLM, concurrencia e interfaces externas.
- Integración AN-KLA condicional mediante contrato, sin dependencia obligatoria.

### B. Adaptación necesaria

- El gate de tamaños debe distinguir la capa interna de la superficie plana de
  artefactos. Enumerar cada publicación en `root_markdown` duplica un catálogo y
  no valida front-matter.
- Los límites de texto de software no deben bloquear fuentes o artefactos cuyo
  tamaño sea contenido de producto; las exenciones deben ser explícitas.
- La estructura `docs/`, `src/`, `tests/`, `scripts/` y `.skevi/` aplica a la
  capa interna. No mueve los artefactos fechados de la raíz.
- La autoridad Git de Skevi queda subordinada a la solicitud humana actual y a
  `AGENTS.md`; ninguna zona local infiere commit o publicación.
- Los archivos metodológicos deben clasificarse como instrucciones de ingeniería
  y excluirse del corpus ingerible por Ágora.
- Toda copia fija commit, ruta y digest por archivo; `v1.1.0` sola no basta.

### C. Burocracia sin beneficio observable

- F0→F3 completo para publicar o corregir un artefacto ordinario.
- ADR para decisiones internas baratas y reversibles.
- Plan de implementación para una sola tarea sin dependencias.
- Reporte en dos capas para tareas triviales o sin consumidor automatizado.
- Revisor externo para cambios editoriales sin disparadores de riesgo.
- Copiar propuestas e historia de Skevi como si fueran norma aplicable.

### D. Conflictos con invariantes de Ágora

- La prohibición genérica de Markdown en la raíz choca con la superficie plana.
- La polaridad cerrada de tamaño para todo texto puede bloquear artefactos
  legítimamente extensos.
- Una copia normativa sin precedencia declarada competiría con `AGENTS.md`.
- Si los documentos Skevi entran al corpus de fuentes, datos no confiables e
  instrucciones operativas quedarían mezclados.
- Los gates estructurales pueden producir apariencia de conformidad sin validar
  semántica L0…Ln, provenance, consolidación o calidad de modelos.

### E. Estado de adopción

Ágora no debe declararse todavía adoptante formal. Skevi define la adopción
mediante copias, registro `.skevi/installed.json`, límites propios y gates. Antes
hace falta un perfil local cerrado que enumere archivos copiados, cláusulas
vinculantes, desviaciones, precedencia, verificación, caducidad y reversión.

## Capacidades, coste y eliminación

| Capacidad | Problema | Mecanismo | Coste | Fallo evitado | Evidencia existente | Eliminar o reducir cuando |
|---|---|---|---|---|---|---|
| Clasificación proporcional | Proceso excesivo o insuficiente | Spike/Bounded/Architectural por disparadores | Clasificar cada tarea | Llamar trivial a un cambio material | ADR-009; piloto Skopos registró cuatro clasificaciones subjetivas fallidas | La telemetría muestre una sola clase efectiva sin diferencias de defecto |
| F0→F3 | Construir antes de entender | Gates secuenciales con evidencia | Latencia y documentos | Features fantasma y contratos tardíos | Piloto infosalud y autoaplicación; evidencia del mismo ecosistema | Un flujo más corto conserve o mejore defectos, tiempo y trazabilidad |
| ADR | Perder el porqué de decisiones caras | Registro inmutable y supersession | Mantener índice y cierres | Reabrir decisiones sin contexto | Veinte ADR publicados; evidencia mayormente interna | Una decisión sea reversible, local y no cree frontera |
| Specs | Requisitos ambiguos | Casos testables, errores e invariantes | Diseño previo | Tests que no cubren contrato | Guía F1 y trazabilidad SPEC→test | REQ y test expresen completamente un cambio simple |
| Proposals | Confundir deliberación con norma | Separar propuesta, decisión e historia | Movimiento y enlaces | Ejecutar ideas no aceptadas | Historia PROP-001…008 | No existan alternativas reales ni decisión pendiente |
| Planes verificables | Perder dependencias entre tareas | Consumes/Produce/Steps + gate | Actualización del plan | Orden imposible y DoD duplicado | `check_plans` OK sobre 2 planes; ADR-014 | El trabajo sea una sola tarea independiente |
| Límites de tamaño | Editar desde lectura parcial | Límites y exenciones cerradas | Partir o justificar archivos | Contradicciones dentro de archivos no leídos | `check_sizes` OK sobre 95 archivos; tests publicados | Ventanas/herramientas midan cobertura completa y no haya defectos correlacionados |
| Hogares canónicos | Duplicar norma y evidencia | Carpetas por vida útil y fuente única | Navegación y referencias | Dos versiones activas | ADR-002; evidencia cualitativa | Un catálogo generado preserve unicidad sin jerarquía manual |
| Fail-closed | Convertir incertidumbre en éxito | BLOQ y salida no cero por clase protegida | Bloqueos y diagnóstico | Publicación o persistencia no verificadas | Gates y 110 tests del snapshot | Un control equivalente demuestre menor bloqueo sin falsos OK |
| Plantillas versionadas | Copias sin procedencia | MANIFEST, digests, versión y `installed.json` | Resync manual | Drift incompatible invisible | ADR-020 y `plantillas/v1`; sin salto real todavía | No se copien plantillas o un gestor garantice contenido exacto |
| Autoridad Git graduada | Fricción local y efectos externos accidentales | Z1–Z3 y dossier | Registro de aceptación | Inferir push/merge/release | ADR-017 y ciclo de PR interno; Ágora sin protección | El host aplique permisos equivalentes con recibos auditables |
| Reportes en dos capas | Mezclar audiencia humana y máquina | Capa técnica + proyección humana | Duplicación y hashing | Parsers sobre prosa o resumen sin evidencia | Dos reportes piloto; parser externo pendiente | No exista consumidor automatizado o el formato estructurado genere más divergencia |
| Ronda adversarial | Sesgo del autor | Ataque posterior a verificación | Otro ciclo de revisión | Tests verdes que no prueban el requisito | Hallazgos de pilotos y esta ronda | Mediciones muestren coste mayor que defectos materiales evitados por clase |
| Independencia del revisor | Autocertificación | Sesión/modelo/contexto separado | Tiempo, cuota y handoff | Repetir el marco mental del autor | Guía F3; evidencia de independencia sigue autodeclarada salvo rastro externo | Cambios sin persistencia, LLM activo, concurrencia ni interfaz externa |
| Provenance/evidencia | Afirmaciones irreproducibles | Comando, resultado, revisión y enlaces | Captura y mantenimiento | Declarar OK por memoria | Gates reproducidos sobre `b400b85` | El entorno capture evidencia equivalente automáticamente |
| AN-KLA opcional | Perder continuidad entre sesiones | Contrato condicional, preflight y checkpoint | Operación de memoria | Usar recuerdos como estado actual | ADR-019; warning actual detectado correctamente | No haya trabajo multisesión o otro sistema cubra la misma continuidad y assurance |

## Incidente: captura de autoridad obsoleta

Skevi reduce el riesgo con jerarquía de fuentes, lectura completa, ADR inmutable
y supersession. No previene suficientemente este incidente: el
`AGENTS.md` antiguo era realmente la instrucción de mayor prioridad y contradecía
un borrador posterior. Seguir la jerarquía llevaba al error; más contexto no lo
corregía.

Mecanismo mínimo propuesto:

1. Una decisión vigente declara explícitamente qué claim y fuente sustituye.
2. `AGENTS.md` contiene sólo la definición operacional vigente y enlaza esa
   decisión.
3. Un fixture de regresión léxico busca exclusivamente las formulaciones
   obsoletas conocidas fuera de secciones marcadas como historia/supersession.
   No es una solución general ni detecta paráfrasis.
4. Un contrato estructural identifica la decisión efectiva y la cadena de
   supersession por `authority_scope`; no infiere vigencia por fecha, ubicación
   ni prosa y no requiere un reasoner semántico.

## Ronda adversarial separada

Revisor: otra sesión/modelo sin acceso a la conversación. Independencia del
revisor: externa al autor; independencia de contexto: fresca; acceso a fuentes:
dossier cerrado; verificación efectiva de fuentes: ninguna; proveedor: Anthropic;
modelo: no observado; ambiente: CLI headless sin acceso concedido al filesystem.
Constituye razonamiento adversarial externo, no verificación independiente de
las fuentes.

Hallazgos aceptados:

- **BLOCKER:** el gate de tamaños colisiona con la superficie plana si se copia
  sin perfil; separar capa interna y artefactos.
- **BLOCKER:** la lista de archivos a copiar y la inclusión de checkers/tests no
  estaban definidas.
- **BLOCKER:** tag y commit no bastan sin manifiesto de rutas y digests.
- **HIGH:** Skevi no cubre semántica L0…Ln, consolidación, no determinismo ni
  evaluación; presentarlo como cobertura arquitectónica sería engañoso.
- **HIGH:** faltaban listas cerradas de cláusulas importadas y no importadas,
  precedencia normativa, exclusión de ingesta y reversión del piloto.

Ataque de hipótesis:

| Hipótesis | Resultado adversarial |
|---|---|
| H0: Skevi no mejora operacionalmente Ágora | Plausible; no hay piloto Ágora. Obliga a medir antes de adoptar definitivamente |
| H1: modelos actuales vuelven innecesarios ADR/spec/gates | No soportada bajo el incidente observado: disponer de contexto no impidió capturar autoridad obsoleta; no falsada universalmente |
| H2: AN-KLA vuelve redundante Skevi | No soportada para las responsabilidades observadas: AN-KLA aporta continuidad/assurance y no cubre por sí solo arquitectura, specs ni gates |
| H3: Skevi + AN-KLA duplica autoridad | Confirmada sólo como posibilidad estructural: se evita asignando autoridad por dominio y conservando en memoria únicamente punteros cuando corresponda; no se ha observado aún un incidente de duplicación |
| H4: rondas cuestan más que los defectos evitados | Posible para tareas triviales; deben activarse por disparadores y medirse |
| H5: más contexto resolverá el problema | No soportada bajo el incidente observado: el contexto incompatible reforzó la premisa; no falsada para toda tarea o modelo |
| H6: cumplimiento documental sin mejor software | Confirmada sólo como riesgo estructural observado; no evaluada todavía sobre software funcional de Ágora |

Decisión de la ronda: **FIX-AND-RETRY** para una adopción formal inmediata.

## Dictamen

**PILOTO, aceptado provisionalmente por el humano.** Preparar un perfil
`agora-skevi-pilot/v1` para la primera rebanada
vertical, sin copiar ni construir todavía. El perfil debe tener precedencia,
archivos y digests exactos, desviaciones con caducidad, gates aplicables,
exclusiones, métricas de coste/defectos y criterio de reversión. Sólo la evidencia
del piloto permite decidir después `ADOPTAR CON PERFIL` o `NO ADOPTAR`.
