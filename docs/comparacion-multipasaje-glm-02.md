# Comparación multipasaje glm-02 — 2026-09-22

Resultado: diagnóstico de acceso resuelto para esta ejecución y comparación
completada, con fallos conservados. No aceptación general del sistema.
Actualiza el estado experimental pendiente de `consulta-multipasaje.md` sin
reescribir los resultados históricos glm-01. No modifica algoritmo, prompt ni
corpus tras observar respuestas; sin commit/push de este informe.

## Acceso al proveedor

Prueba mínima sintética provider-diagnostic-01 con la credencial recibida por el
proceso: HTTP401, una solicitud. La clave configurada previamente en el laboratorio
era distinta; no se mostró ni copió a artefactos. Se inyectó sólo al proceso.
provider-diagnostic-02 respondió correctamente «El código es AZUL»; modelo
solicitado/reportado glm-5.3-flash;561tokens reportados. Sin configuración global
modificada. Estas observaciones no prueban la causa de los dos HTTPError de
la corrida histórica glm-01, donde no se conservó código HTTP.

## Método y procedencia

Mismo corpus sintético14.543bytes y cinco preguntas conocidas. Tres rutas:
fuente completa, pasajes preseleccionados y recuperación léxica con vecinos.
Copia de código y protocolo congelada antes de ejecutar,13archivos verificados.
15rutas finalizadas,14solicitudes, sin reintentos; Q3-retrieve no tuvo candidatos.
Modelo pedido/reportado glm-5.3-flash en las14respuestas; el reporte del proveedor
no constituye identificación independiente del modelo subyacente.
Una repetición por ruta: no estabilidad ni generalización estadística.
Fuente y referencia no comparten presupuesto de contenido:20480y1800bytes;
recuperación1800bytes. Mismo prompt,2048tokens de salida,temperatura0.

## Evaluación contra los criterios previos

| Caso | Fuente completa | Referencia preseleccionada | Recuperación |
|---|---|---|---|
| Q1 plazos contradictorios | Inferencia no respaldada | Cumple | Cumple |
| Q2 responsable y partida distantes | Cumple | Cumple | Cumple |
| Q3 sinónimos | JSON inválido, rechazado | Cumple | No recupera evidencia |
| Q4 importe ausente | Abstención adecuada | Abstención adecuada | Abstención adecuada |
| Q5 responsable local | Cumple | Cumple | Cumple |

Fuente:3/5;referencia:5/5;recuperación:4/5. Son conteos de estas tareas, incluyendo
abstención correcta enQ4; no porcentajes generales de fidelidad o recall.

Q1-source contiene números/citas correctos, pero agrega «ambos plazos figuran
vigentes en el documento». No declarar sustitución no acredita vigencia conjunta.
La fuente completa no es verdad de referencia ni evita esa inferencia.
Q3-source conserva salida rechazada: JSON inválido confirmado sin repararlo;
adicionalmente incluye una cita de mobiliario irrelevante. No se contabiliza
como respuesta correcta aunque su texto visible incluya la idea buscada.
Q3-retrieve no demuestra ausencia: existe evidencia que el buscador léxico pierde.

Dictamen separado de review_large_source_plan contrastado con fuente/criterios.
Es otro agente del mismo entorno, no auditoría externa ni adjudicación del Operador.
Los resultados originales mantienen sus estados; review.json registra la revisión
por separado, vinculada a hashes. No admisión a memoria ni decisiones automáticas.

## Recursos observados

| Ruta | Solicitudes | Tokens totales reportados | Tiempo acumulado de procesos |
|---|---:|---:|---:|
| Fuente completa |5|20993|41,252s|
| Referencia preseleccionada |5|3678|40,053s|
| Recuperación |4|3733|30,321s|

Incluye uso del resultado rechazado. Tabla sólo glm-02:28404tokens reportados.
Diagnóstico exitoso adicional561tokens; total conocido de esta continuación28965.
La solicitudHTTP401no reportó uso: consumo desconocido, no cero.
No se consultaron precios: no se afirma coste monetario. Los tokens incluyen
entrada/salida; el proveedor reportó caché en varias entradas. La latencia incluye
arranque/preparación local y proveedor, no preparación humana ni revisión.

Comparación de preguntas comunes Q1/Q2/Q4/Q5, excluyendo Q3en todas las rutas:
fuente16513tokens/24,610s;referencia3060/33,628s;recuperación3733/30,245s.
Así no se contabiliza el fallo sin llamada como ahorro a igual resultado. Aun
este subconjunto no iguala calidad: fuente fallaQ1. No hay prueba de superioridad
general. Menos tokens tampoco implicó menor tiempo en el subconjunto común.
La referencia manual tiene trabajo de selección previo no valorado monetariamente.

## Evidencia local y reproducción

`experiments/passage-comparison-v1/runs/glm-02/`: freeze.json, código ejecutado,
fuente/casos/protocolo, resultados por ruta, execution.json, metrics.json,
review.json y provider-configuration.json sin clave. Hashes de13archivos congelados
y15resultados comprobados; implementation_unchanged=true en las15rutas.
Diagnósticos guardados en provider-diagnostic-01 y02. Todos en runs/, ignorado por
Git. Su existencia local no equivale a publicación; documentos privados no usados.
No se repitieron pruebas de código porque no hubo cambios de producto; las99pruebas
previas corresponden al código ejecutado, no son un nuevo resultado de esta tarea.

## Decisión técnica propuesta

1. Mantener fuente, referencia y recuperación como rutas explícitas. No promover
   búsqueda léxica como sustituto general de lectura.
2. Siguiente incremento acotado: recuperación adicional cuando no haya candidatos,
   con presupuesto y procedencia explícitos. Fuente completa sólo si cabe; si no,
   solicitar otra estrategia o declarar insuficiencia, nunca truncar silenciosamente.
3. Conservar validación de JSON y citas; no reparar automáticamente el falloQ3ni
   añadir reglas específicas para obtener éxito retrospectivo en este corpus.
4. Evaluar el mecanismo nuevo con casos diferentes antes de atribuir generalización.
   Mantener revisión semántica: un fallback a fuente completa también puede fallarQ1.
5. Skopos/AN-KLA siguen como adaptadores posteriores; el cuello actual es recuperar
   evidencia suficiente y revisar interpretaciones, no conectar más componentes.
