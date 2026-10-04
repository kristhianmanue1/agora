# Banco de errores controlados v1

## Propósito

Calibrar al revisor (Jev) con fallos pequeños pero decisivos antes de confiarle
decisiones de aceptación. Cada error inyectado tiene un **gemelo correcto**: misma
fuente y pregunta, respuesta válida. No es una comparación MemOS/Ágora ni una
batería reservada. Su construcción no consumió llamadas a modelos; la ejecución
con Jev es un paso posterior con presupuesto propio.

## De dónde sale cada error

Ningún caso es hipotético puro: cada familia reproduce un fallo ya observado en
las campañas previas, simplificado hasta hacerlo verificable a mano.

| Familia | Origen observado | Qué pone a prueba |
|---|---|---|
| `metric_swap_cited` | v2: Ágora invirtió precisión/recall con cita literal válida | Que validar una cita no implique validar las cifras |
| `study_merge` | v3: MemOS presentó HiStGen/WIKIOG como trabajos separados/uno | Atribución correcta de resultados a cada trabajo |
| `qualifier_scope` | v2: pruebas cualitativas cotidianas presentadas como validación | Conservar calificadores que cambian la fuerza del claim |
| `question_ambiguity` | v3: «mejora» de diálogo frente a mejora del clasificador | Hacer visible la ambigüedad en vez de resolverla en silencio |
| `scope_generalization` | v2: «no hay baselines» concluido desde lectura parcial | No generalizar ausencia desde pasajes recuperados |
| `backing_vs_coverage` | refinement-v1: Jev falló dos veces la celda supported+omitted | Separar «está respaldado» de «contesta lo pedido» |

## Inventario

Doce controles: seis errores y seis gemelos correctos. Distribución de etiquetas
esperadas por celda (respaldo × cobertura):

| | complete | omitted |
|---|---:|---:|
| supported | 5 | 2 |
| unsupported | 1 | 4 |

La celda `supported + omitted` —la única donde Jev falló en refinement-v1— tiene
dos casos nuevos de dominios distintos (`backing_vs_coverage` error y
`scope_generalization` control, este último además con `declared_partial_scope`).

Campos por control: `id`, `family`, `variant` (error/control), `origin`,
`source`, `retrieved` (solo `scope_generalization`: pasajes que vio el
respondedor), `question`, `answer`, `expected_support`, `expected_coverage`,
`expected_flags`. Las etiquetas y los flags **nunca se envían al revisor**; los
flags son diagnóstico del productor, no ejes de Jev. Los IDs son deterministas:
once caracteres hexadecimales de `sha256(family|variant)`.

## Protocolo de ejecución (cuando se apruebe)

1. Máximo cuatro llamadas Jev, tres controles por llamada, familias mezcladas.
2. Orden directo y orden inverso; las etiquetas esperadas permanecen fuera del
   contexto en ambos. Cero reintentos.
3. Jev recibe fuente completa (y, si el caso la declara, la lista de pasajes
   recuperados), pregunta y respuesta, sin nombres de productor.
4. Registrar todas las salidas, incluidas las probabilidades del proveedor,
   como en refinement-v1.

## Umbral de promoción

- Al menos **23/24 parejas de etiquetas correctas en cada orden**.
- **Cero fallos en la celda `supported + omitted`** en ambos órdenes.
- Los cinco gemelos completos (`supported + complete`) aceptados en ambos órdenes.

Superar el umbral no promociona a Jev automáticamente: exige confirmación del
productor y una nueva ronda reservada con adjudicación separada. Los seis
controles de `../refinement-v1/` se conservan como regresión y siguen formando
parte de cualquier decisión posterior.

## Límites

Controles sintéticos escritos por el productor: miden la conducta del revisor
ante patrones de error conocidos, no la calidad media de respuestas reales ni la
verdad de las fuentes. La adjudicación sigue siendo del productor. Ningún
documento QASPER se reutiliza; las fuentes del banco son ficticias y cortas
para que el veredicto sea auditable a mano.

## Evidencia

- `controls.json`: los doce controles, con hash fijado en `freeze.json`.
- `freeze.json`: hash, presupuestos y reglas congeladas antes de ejecutar.
- Los resultados de la ejecución se añadirán en un expediente separado;
  este banco no se reescribe después de correr Jev.
