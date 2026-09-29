# Controles negativos sobre fragmentos del manual DPM

Batería sintética de desarrollo autorizada por el Operador. Siete llamadas como máximo a Jev, 90 segundos cada una, sin reintentos. Se reutilizan exactamente los fragmentos ya enviados en plan-ids-review-v1; sólo cambian las afirmaciones. No se modifica el generador ni el revisor predeterminado.

Tres controles positivos, una atribución al encabezado equivocado, eliminación explícita de autorización previa, ampliación de ámbito institucional y una omisión inocua. Los casos y las etiquetas se congelan antes de llamar al proveedor. El runner no lee gold.json; sólo envía pregunta, evidencia y afirmación. Entradas y respuestas completas quedan excluidas de Git. freeze.json registra hashes, presupuesto y criterio previo.

Criterio principal: rechazar como supported las tres alteraciones sin rechazar los cuatro controles respaldados. La coincidencia de etiqueta exacta se informa por separado. Etiquetas del productor, no adjudicadas independientemente; no es una batería reservada ni mide prevalencia real, completitud documental o rendimiento comparativo con GLM.

Autorrevisión adversarial del diseño: atribuir una función a otra unidad podría ser mera falta de evidencia, por lo que el caso pregunta expresamente qué atribuye el fragmento 7.1.2. La ampliación de alcance se etiqueta insufficient, no contradicted. Una omisión de autorización sólo se convierte en contradicción cuando se afirma que no hace falta; el control de omisión evita equiparar resumen incompleto con afirmación falsa.

Ejecución: inyectar TYPESAFE_API_KEY mediante Llavero y ejecutar `python3 experiments/plan-ids-negative-v1/run.py jev --out experiments/plan-ids-negative-v1/runs`. El runner rechaza entradas con hash distinto y una carpeta runs existente. No repetir una corrida sin inspeccionar primero su journal.

## Estado de ejecución

Preparado y comprobado localmente; cero llamadas realizadas. La revisión automática bloqueó el envío porque requiere autorización explícita del payload nuevo de siete casos a Typesafe/Jev. La autorización general para continuar no se interpretó como autorización suficiente de esta transferencia. Inputs locales en `inputs/cases.json`; etiquetas separadas en `gold.json`. No hay resultados semánticos nuevos ni promoción del revisor.
