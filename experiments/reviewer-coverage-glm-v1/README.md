# Contraste de suficiencia: GLM frente a Jev

## Resultado

Diez revisiones GLM glm-5.3-flash sobre los mismos estados de cobertura del [ensayo separado](../reviewer-separated-v1/README.md), sin regenerar respuestas. Todas terminaron y devolvieron etiquetas válidas.

| Grupo | Jev previo | GLM nuevo |
|---|---|---|
| Tres abstenciones honestas pero insuficientes | complete en 3/3 | omitted en 3/3 |
| Tres controles positivos | complete en 3/3 | complete en 3/3 |
| Dos negativos sintéticos | omitted en 2/2 | omitted en 2/2 |
| Pregunta ambigua: cuotas iguales | complete | complete |
| Pregunta ambigua: redistribución | complete | omitted |

GLM coincide con **8/8 expectativas fijadas del productor**, Jev con 5/8. Los dos candidatos ambiguos no forman parte de ese denominador. Frente a la intención reflejada en las referencias QASPER, ambos omiten identificar la arquitectura; GLM conserva un falso completo en cuotas iguales. No se redefine el denominador para ocultarlo. La coincidencia de dos modelos en complete para ese candidato no lo vuelve correcto.

**Decisión:** GLM queda como candidato experimental para suficiencia, sin sustituir el revisor predeterminado ni activar aceptación automática. Jev conserva evidencia favorable acotada para fidelidad aislada, pero no se promueve una combinación de revisores por escoger sus mejores resultados en la misma muestra.

## Comparabilidad y procedencia

Se conservan exactamente los diez estados task/answer/full_source y su orden. score.py comprueba igualdad textual con el state enviado previamente a Jev. Reutiliza los mismos criterios e instrucciones de coverage. La API GLM recibe esos criterios en el system prompt y exige un objeto JSON; Jev recibió preguntas tipadas. No es el mismo mecanismo de inferencia ni un ensayo concurrente aleatorizado.

No se transmitieron método de recuperación, grupos, referencias externas, expectativas, etiquetas anteriores ni otros candidatos. Las entradas son cinco artículos públicos QASPER y respuestas de prueba, incluidos dos controles alterados explícitamente. Antes del envío se comprobó que los textos coinciden byte a byte con el render del dataset cuyo hash coincide con la selección original. La revisión automática inicialmente rechazó el envío por posible contenido privado; tras aportar esa verificación y la autorización vigente permitió la ejecución. El rechazo inicial no lanzó llamadas ni creó el ensayo.

freeze.json fija diez llamadas, modelo, temperatura 0, salida máxima 2.048 tokens, timeout 90 s y cero reintentos. Se utiliza Llavero para inyectar la credencial; no se publican secretos. Los registros de solicitudes y textos completos quedan ignorados. Los originales y sus etiquetas permanecen intactos.

## Consumo observado

| Sólo revisión de cobertura, diez casos | Jev previo | GLM nuevo |
|---|---:|---:|
| Tokens entrada | 76.415 | 70.747 |
| Tokens salida | 532 | 4.183 |
| Total reportado | 76.947 | 74.930 |
| Segundos acumulados de solicitudes | 3,632 | 80,301 |

Los tokenizadores y mecanismos son distintos; estos números no equivalen a coste monetario comparable ni ahorro demostrado. Los tiempos no incluyen todo el trabajo de preparación ni representan latencias generales de los servicios. GLM fue más lento en este lote. No hubo fallos ni uso desconocido.

## Autorrevisión adversarial y límites

- **Muestra conocida:** ocho controles con expectativas del productor, elegidos tras fallos previos, no batería reservada ni evaluación independiente.
- **Conflicto de origen:** GLM pertenece a la familia que generó candidatos. Evaluar una salida propia conservada en una solicitud nueva no demuestra independencia. Las referencias externas ayudan a contrastar, pero tampoco son infalibles.
- **Ambigüedad no resuelta:** persiste el complete sobre procedimiento de entrenamiento cuando QASPER pide identificar el modelo. Cambiar de revisor no fija por sí solo la intención.
- **Resultado acotado:** 8/8 controles favorece este candidato en suficiencia, no implica que sea mejor para fidelidad, contradicciones, documentos distintos o aceptación automática.
- **Cambios de interfaz y momento:** criterios y estado iguales, pero payload y protocolo de proveedor distintos; no se atribuye causalmente toda diferencia al modelo.
- **Sin consenso como verdad:** ante desacuerdo se vuelve a fuente y pregunta; ante acuerdo también puede existir error compartido.

## Próximo paso recomendado

Congelar esta configuración de suficiencia y someterla a una pequeña batería **reservada nueva**, sin ajustar el prompt con sus resultados. Separar por adelantado preguntas claras de ambiguas usando contexto documental y referencias, sin mostrar candidatos al definir esa clasificación. Incluir respuestas adecuadas, omisiones, abstenciones y falsedades; mantener verificación de procedencia local.

Antes de integración en CLI, contrastar contra referencias y revisar desacuerdos. Si se prueban GLM y Jev, hacerlo sobre la misma batería y declarar el conflicto de origen de GLM. Mantener los resultados como candidatos: una etiqueta complete nunca equivale a admisión de memoria ni decisión humana. No se ejecutó esa batería nueva en este turno.

## Reproducción local

prepare.py crea entradas a partir del ensayo separado; run.py realiza solicitudes y no debe repetirse sobre este lote. score.py verifica hashes, requests y estado idéntico, y recompone resultados sin llamar a proveedores. Se verificó compilación, reproducción determinista y enlaces documentales. No se repitió la suite de producto porque no se modificó código de producto.
