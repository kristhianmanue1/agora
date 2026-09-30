# Materialidad: requisitos explícitos y controles de paráfrasis

## Resultado

**12/12 casos coinciden exactamente con las expectativas fijadas**, sin aceptar como cubierto ningún requisito omitido o contradicho. Son 30 clasificaciones por requisito, agrupadas en 12 casos correlacionados de dos documentos públicos conocidos. No son 30 observaciones independientes ni una batería reservada.

| Grupo de controles | Resultado |
|---|---|
| Candidato real conservado y paráfrasis equivalente | R1/R2/R3 cubiertos |
| Falta de composicionalidad | R3 ausente; R1/R2 cubiertos |
| Sólo contexto de origen de las métricas | Los tres requisitos ausentes |
| Correlación invertida | R1 contradicho; R2/R3 cubiertos |
| Paráfrasis con contexto adicional | Tres requisitos cubiertos; no penaliza ampliación |
| Misma respuesta, pregunta añade origen de métricas | R4 ausente |
| Respuesta incorpora origen solicitado | Cuatro requisitos cubiertos |
| Transferencia a poda: paráfrasis / inversión / vaguedad / extra correcto | Cubierto / contradicho / ausente / cubierto |

GLM glm-5.3-flash reportado, temperatura 0, 2.048 tokens máximos de salida, 90 s y cero reintentos. Doce llamadas terminadas. Consumo: **10.991 tokens** (8.252 entrada, 2.739 salida), 58,601 segundos acumulados de solicitudes. No coste monetario verificado.

## Qué se definió

rubric.json fija una rúbrica experimental del productor para la pregunta sobre limitaciones de métricas de diálogo:

- R1: correlación débil de perplexity/BLEU con juicios humanos.
- R2: diversidad de respuestas válidas y necesidad de numerosas referencias para BLEU.
- R3: promedios de embeddings insuficientes para composicionalidad de oraciones.
- R4 aparece sólo en la variante que solicita explícitamente el origen en traducción automática.

Cada requisito lleva evidencia de la fuente; R1–R4 incluyen offsets verificables sobre QASPER 1803.08419. La transferencia usa un requisito de poda respaldado por QASPER 1606.07947. Pregunta, candidato, requisitos y evidencia se envían al revisor; etiquetas esperadas y grupos de control quedan fuera.

El proveedor devuelve únicamente IDs suministrados y estados covered/missing/contradicted/uncertain. La validación local comprueba cobertura exacta de IDs. No puede introducir silenciosamente un nuevo requisito obligatorio. Esta restricción reduce ampliaciones, pero también hace invisible un requisito importante que falte en la rúbrica.

## Método y límites

La rúbrica y expectativas se congelaron antes de las llamadas. Se reutilizó un candidato real, y el resto son variantes redactadas por el productor. No hubo generación nueva de respuestas ni modificación de candidatos anteriores. El producto y su diagnóstico abierto no cambian: esto es un ensayo separado, no una mejora ya integrada.

La selección de tres requisitos se apoya en fuente, pregunta y anotaciones QASPER alternativas; no se presentó como unión obligatoria de todas las anotaciones ni como adjudicación del Operador. El control de cambio de pregunta evita declarar el origen de métricas siempre irrelevante: se vuelve obligatorio cuando se solicita.

**Lo demostrado:** con esta rúbrica fija y estos casos, GLM distingue ausencia, contradicción, paráfrasis y contexto adicional según las expectativas del productor.

**Lo no demostrado:** descubrimiento automático de todos los requisitos, calidad de otras rúbricas, fidelidad global de afirmaciones fuera de requisitos, generalización a documentos reservados o precisión independiente. Dar al revisor requisitos con evidencia es deliberado; no equivale a evaluar un diagnóstico abierto sin guía. No se compara causalmente el consumo con ensayos de fuente completa: aquí la selección de evidencia y construcción de rúbrica están hechas fuera del modelo y no contabilizadas como coste automático.

## Autorrevisión adversarial

- Una rúbrica incompleta produce una respuesta aparentemente completa: el principal riesgo se desplaza a definir requisitos y alcance.
- Los casos son sencillos, conocidos y relacionados. 12/12 no habilita promoción por sí solo.
- La forma permite exigir sólo IDs conocidos, pero esa comprobación no valida semánticamente ni autoriza los requisitos.
- El ensayo no elimina los dos diagnósticos anteriores ni cambia su valoración retrospectivamente. Conserva desacuerdos y procedencia.
- No hubo revisor independiente; la autorrevisión separa expectativa del productor, predicción y evidencia literal.

## Siguiente paso recomendado

Introducir una **rúbrica opcional versionada y ligada por hash a pregunta y fuente**, explícitamente seleccionada por el usuario, como modo experimental separado. Conservar quién la propuso y si su completitud está pendiente; no convertirla en autoridad ni sustituir silenciosamente la pregunta o el diagnóstico abierto. La salida debe mostrar “cubierto respecto de esta rúbrica”, nunca “documento completo”.

Antes de integrarla, validar cambios de pregunta, fuente y rúbrica; rechazar discrepancias y añadir un control con rúbrica deliberadamente incompleta para que el límite sea visible. Mantener evaluación de omisiones fuera de rúbrica como revisión separada, sin agregar obligaciones automáticamente. No se implementó esa integración en este lote.

## Verificación

score.py verifica hashes de entradas, rúbrica y etiquetas congeladas, coteja requests reales y recompone métricas. Se comprobaron los offsets de evidencia, compilación de scripts y enlaces documentales. Sin cambios de producto, no se repitió la suite de 483 pruebas del commit precedente. Los textos de entrada y journals completos permanecen ignorados; el revisor no recibe etiquetas esperadas.
