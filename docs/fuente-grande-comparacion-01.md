# Fuente grande: ahorro puntual y omisión en visión global

2026-09-23. Comparación parcial: tres respuestas y un timeout. No se modificó
el producto. Evidencia local: `experiments/large-source-v1/runs/glm-01`.

## Fuente y protocolo

Se seleccionó el documento más largo del test QASPER v0.3 local:
`1810.13414`, *Extracting Linguistic Resources from the Web for Concept-to-Text
Generation*, 138223 bytes UTF-8. No figuraba en pilot-01 ni pilot-02. Fuente:
QASPER, Dasigi et al., NAACL 2021, dataset CC-BY 4.0. El archivo de entrada se
verificó contra su hash previamente registrado. Se conserva la representación
del corpus con marcadores INLINEFORM/TABREF; no se evaluaron cifras de tablas
no disponibles en esa representación. No se verificó el PDF editorial.

Dos preguntas propias y sus criterios se fijaron antes de llamadas. No son
preguntas puntuadas por el evaluador oficial ni un benchmark independiente.
La selección posterior a examinar secciones y referencias es desarrollo.

Se usó el mismo consumidor `passage_cli` en ambas rutas, con su prompt base
legacy y respuestas en español. No es un ensayo del prompt adicional de
`routed_cli`. GLM solicitado/reportado: `glm-5.3-flash`, temperatura 0,
response_format omitido, salida máxima 8192 tokens, socket 90 s/proceso 110 s.
Fuente directa: presupuesto 160000 bytes. Recuperación léxica: 12000 bytes,
top_k 3, expansión a párrafos vecinos. Prompt máximo 200000 bytes.
Cuatro llamadas como máximo, sin reintentos; orden alternado por pregunta.
Código, entradas, criterios y ejecutor congelados antes de llamar al proveedor.

## Resultados

| Tarea/ruta | Texto fuente enviado | Tokens totales | Segundos | Resultado |
|---|---:|---:|---:|---|
| M1/directa | 138223 B | 33034 | 34.649 | Aceptada; criterios conservados |
| M1/recuperación | 6757 B | 3010 | 16.160 | Aceptada; criterios conservados |
| G1/recuperación | 5478 B | 4218 | 66.235 | Aceptada; omisiones materiales |
| G1/directa | 138223 B | desconocido | 90.644 | Timeout |

M1 pide ontologías, comparación de configuraciones y debilidad de m-piro.
Ambas respuestas conservan Wine/m-piro/Disease; manual mejor, semi-auto cercano
sin diferencia significativa detectada en muchos casos, auto mucho peor; y
el problema de pocas semillas que afecta semántica y claridad de m-piro.
Recuperación consumió 90.9% menos tokens en este par. No hubo llamadas LLM de
indexación ni extracción: sólo una llamada de respuesta por ruta. Sin embargo,
la búsqueda local sí escanea los 138223 bytes completos y el adaptador también
relee/verifica la fuente. Es ahorro de contexto del modelo, no de toda lectura
local ni demostración de escalabilidad a documentos arbitrarios.

M1 pretendía unir partes del documento, pero la sección de experimentos conjuntos
repite suficiente información para contestarla. Por eso no acredita una unión
difícil entre secciones. G1 sí requiere detalles distribuidos del método y límites.

## G1: formato correcto, contenido incompleto

Criterios definidos previamente y revisión contra texto:

| Criterio | Recuperación limitada |
|---|---|
| Nombres: frases nominales, alineación con identificadores, anotaciones | Omite el procedimiento |
| Planes: plantillas/semillas, anotaciones, clasificador Maximum Entropy | Omite el procedimiento |
| Selección humana entre cinco frente a primer candidato automático | Omite la regla |
| Resultado semiautomático y limitación totalmente automática | Conserva |
| Otros recursos manuales en todas las configuraciones, especialmente text plans | Parcial: menciona text plans como trabajo futuro, no el control experimental |
| Lenguas distintas del inglés como trabajo futuro | Conserva |

El recuperador eligió sobre todo resumen, introducción y conclusiones. No incluyó
los pasajes específicos de métodos ni el párrafo que fija los otros recursos
manuales. La respuesta contiene afirmaciones respaldadas, pero no satisface la
solicitud completa y no explicita esos huecos. La aceptación del contrato y
`candidate` **no detectan esta incompletitud semántica**.

No se concluye que la lectura directa resolviera G1: su llamada agotó el timeout.
Los cuatro intentos se registraron; sólo tres entregaron respuesta. El consumo
total es **40262 tokens conocidos más el consumo desconocido del timeout**.
Los procesos sumaron 207.688 segundos; preparación y revisión humana no están
incluidas en ese tiempo. No se midió coste monetario. No hay ahorro global
cuantificable para toda la campaña ni comparación temporal generalizable.

## Verificación y autorrevisión

Las quince citas aceptadas (M1: 3 y 4; G1 recuperada: 8) coinciden con los bytes
de la fuente. Se contrastaron respuestas y criterios manualmente; revisión del
mismo productor, no independiente. El respaldo literal no demuestra por sí
mismo cobertura, inferencia correcta ni exhaustividad.

`audit.py` verifica manifiesto congelado, hashes de respuestas, código vigente
contra el ejecutado y rangos UTF-8 de cada cita. Sintaxis y `git diff --check`
pasaron. No se cambió código del producto ni se repitió su suite: la evidencia
previa de 183 tests corresponde al mismo código verificado. Los archivos de
fuente, criterios y respuestas permanecen locales, excluidos de Git.

## Continuación recomendada

1. Conservar M1 como regresión de ahorro puntual, sin convertirla en prueba de
   multi-hop ni repetirla para obtener otro resultado favorable.
2. Para G1, ensayar recuperación por cada aspecto solicitado (nombres, planes,
   selección, evaluación, recursos manuales e idiomas), con unión deduplicada y
   presupuesto total fijo. Si un aspecto queda sin evidencia, indicar la laguna
   y solicitar ampliación; no tomar un resumen general por cobertura completa.
3. Medir si esa ampliación recupera los hechos omitidos y su coste adicional.
   Mantener los mismos criterios y reconocer que G1 ya es un caso de desarrollo.
4. Para completar la comparación global con lectura directa, hace falta una
   ejecución separada de G1/directa con límite temporal explícitamente revisado;
   preservar el timeout previo y no incorporarlo como cero tokens.

El siguiente incremento útil es cobertura por aspectos con ampliación acotada,
no más cambios de formato. No requiere conectar Skopos ni AN-KLA para probarlo.

## Seguimiento

La [prueba por aspectos](recuperacion-por-aspectos-01.md) recuperó procedimientos
antes omitidos, pero sigue incompleta. La nueva lectura directa respondió con
más tiempo y fue rechazada por exceder el máximo de citas. Se conservan los
resultados anteriores y no se afirma una baseline global aceptada.
