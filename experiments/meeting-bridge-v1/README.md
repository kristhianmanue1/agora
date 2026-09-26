# Piloto conjunto: fuente vigente de Skopos → candidato de Ágora

Reunión sintética, dos revisiones (lunes→martes), dos fragmentos, responsable,
cantidad y condición de aceptación. Presupuesto monetario no informado.
Persistencia experimental SQLite de Skopos, cierre/reapertura, búsqueda vigente,
exportación verificada y puente por archivo UTF-8 con huella propia. El paquete
conserva localizadores nativos para volver de cada cita al fragmento original.

Máximo tres solicitudes GLM: generar candidato, revisar respaldo, revisar
pertinencia. Modelo glm-5.3-flash, salida 8192 por solicitud (24576 reservados),
HTTP 90 s/proceso 100 s, sin reintentos; parada ante transporte o consumo desconocido.
Datos exclusivamente sintéticos y clave desde Llavero. El ensayo no escribe AN-KLA,
no toca Mongo y no instala adaptadores en servicios de producción.

Criterios: revisión 2 recuperada tras reabrir; lunes excluido de búsqueda vigente;
fecha martes 29, 40 equipos, Nerea y condición conservadas; presupuesto ausente
explícito; cada cita literal navegable al origen revisado. Comprobar el contenido
contra esos hechos separadamente de las etiquetas de los revisores.

Código y entradas se congelan antes de la primera llamada. Hashes de código
identifican el artefacto probado, además de HEAD. La revisión es del mismo proveedor,
no independiente; no se concede aprobación automática. Prueba pequeña, sin escala,
concurrencia ni fuentes privadas. No acredita el conector de reuniones de producción.

## Variante por identificadores — protocolo previo a ejecución 02

Invocar run.py con raíz de Skopos, directorio nuevo y cuarto argumento `ids`.
Sin ese argumento se conserva literal. Se reutiliza el contrato existente de
Ágora: el modelo selecciona IDs de unidades y el código resuelve sus citas desde
la fuente. No se completa ni corrige JSON del modelo. Un ID inexistente o una
salida inválida siguen rechazándose.

Misma reunión, preguntas, modelo y límites (tres solicitudes como máximo,
8192 tokens por solicitud, HTTP 90 s, proceso 100 s, cero reintentos). Cambia sólo
el modo de referencia y su prompt derivado. Conservar ejecución 01 íntegra.
Esta variante reduce copia literal, pero no garantiza JSON válido. Una ejecución
correcta demostraría este recorrido, no superioridad general del formato.
