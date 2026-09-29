# Suficiencia del resumen para una tarea concreta

## Resultado local

Reutilizamos dos respuestas conservadas de Jev (plan-ids-negative-v1): ambas afirmaciones fueron supported. Se verificó que sus requests corresponden exactamente a los casos de origen. No se repitieron llamadas ni se presentó la nueva tarea como parte de la ejecución anterior. Trazabilidad en [replay.json](replay.json).

La tarea nueva pide describir qué hacer antes de instrumentar políticas, quién autoriza y cuándo. El resumen completo conserva esos datos. El breve sólo afirma que la Unidad de Atención Médica define las políticas: es respaldado, pero no responde a la autorización necesaria. Esta insuficiencia es análisis del productor, no resultado nuevo del modelo. Etiquetas congeladas en [gold.json](gold.json).

## Contraste contra código

- `src/agora/evidence_checks.py`: respaldo, relevancia, certeza y alcance de detalles afirmados. No enumera todos los datos que una respuesta debería contener.
- `src/agora/sufficiency.py`: pregunta si los PASAJES permiten responder toda la pregunta. Su input no contiene el resumen candidato; pasar el pasaje completo no detecta por sí mismo una omisión del resumen.
- `src/agora/coverage.py`: cobertura de bytes y juicio semántico separado; cobertura física no demuestra completitud semántica.

Propuesta: distinguir evidence_sufficiency (¿la fuente permite responder?), claim_support (¿lo afirmado está respaldado?) y answer_sufficiency (¿el resumen responde lo indispensable para esta tarea?). Son ejes descriptivos propuestos, no contratos de producto incorporados ni permisos para actuar.

## Piloto preparado

Dos requests a Typesafe/Jev, cada uno con tarea, evidencia y resumen; una elección tipada sufficient/insufficient/uncertain. Modelo jev-1.13.0; dos llamadas máximo, 90 s cada una, cero reintentos. No se envían las etiquetas esperadas. No modifica defaults, admisión ni candidatos previos.

`run.py` reutiliza transporte y journal de reviewer-comparison-v1, con payload y parser experimentales separados. Ejecutado tras autorización explícita del Operador para estos dos casos. Dos llamadas completadas, coincidencia 2/2; véanse [resultados y límites](RESULTS.md). No repetir sobre el journal existente.

## Autorrevisión adversarial

Dos casos de desarrollo, misma fuente, etiquetas del productor y sin independencia. Este par no demuestra generalización ni un benchmark reservado. La tarea menciona explícitamente la autorización; pasar esta prueba no demuestra descubrir por sí mismo requisitos implícitos. La omisión es inocua para identificar una función, pero decisiva para describir los pasos previos a instrumentar: la suficiencia depende de la tarea. Un sufficient del modelo tampoco autoriza una acción ni demuestra vigencia externa del manual.

Siguiente comprobación, si el par pasa: usar una tarea menos dirigida y requisitos críticos fijados antes de la generación; conservar juicios de omisión separados de respaldo. Evitar arreglar el resumen automáticamente con una mera etiqueta.
