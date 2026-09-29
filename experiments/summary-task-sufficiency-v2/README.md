# Suficiencia contextual: tarea menos dirigida

Preparado; cero llamadas. Cuatro casos de desarrollo: resumen completo/breve × tarea operativa/descriptiva. Se conserva el mismo fragmento ya empleado en v1. La tarea operativa no nombra autorización, autoridad ni momento; la descriptiva pregunta qué unidad define las políticas.

## Hipótesis fijada antes de la ejecución

Tres suficientes y uno insuficiente: el breve operativo. La autorización omitida es necesaria para resumir el procedimiento; no es necesaria para identificar la unidad. Etiquetas del productor en gold.json, sin adjudicación independiente. No se cambian después de observar resultados.

## Evidencia e interpretación

La API documenta Choice/Noul/Score; no se presupone texto libre. Se solicitan tres elecciones por caso: sufficiency y clasificación de las unidades e1/e2 (covered, missing_required, not_required, uncertain). Covered tiene precedencia si el resumen conserva el contenido, aun si fuera extra para la tarea. E1 contiene la función de definir; E2 contiene el sometimiento a autorización. Las unidades son subcadenas exactas, con offsets de caracteres sobre el fragmento local, NO offsets UTF-8 sobre el PDF original. Ágora puede resolver sus IDs a esas citas sin inventar explicación del proveedor.

Selección de una cita no prueba por sí sola que el juicio semántico sea correcto. Se informarán inconsistencias (por ejemplo sufficient con missing_required), sin convertirlas silenciosamente en un resultado válido ni reparar el resumen. El parsing sólo comprueba forma.

## Alcance y límites

Máximo cuatro llamadas a Typesafe/Jev jev-1.13.0, 90 segundos cada una, cero reintentos. State: tarea, fragmento, resumen y unidades exactas; gold excluido. Entradas y journals fuera de Git. Requiere autorización explícita del nuevo conjunto, conforme al bloqueo previo por payload. No se ha intentado el envío.

Comparación de desarrollo, una fuente y etiquetas del productor; no benchmark independiente. Separar dos unidades hace visible la estructura: la tarea es menos dirigida, pero esto no demuestra descubrimiento autónomo de requisitos en documentos completos. No mide recuperación, omisiones globales ni capacidad de explicación libre. No cambia defaults ni contratos de producto.

Documentación consultada: https://docs.typesafe.ai/introduction/quickstart (tipos de preguntas y múltiples preguntas por llamada).

## Verificación local

Checks: cuatro casos; hashes congelados; cada unidad coincide con su subcadena; gold no enviado; parser rechaza campos/etiquetas incorrectos. Cero respuestas de modelo nuevas. Ejecutar sólo tras aprobación del envío mediante Llavero: `python3 experiments/summary-task-sufficiency-v2/run.py jev --out experiments/summary-task-sufficiency-v2/runs`.
