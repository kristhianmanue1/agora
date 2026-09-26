# Recorrido acotado con evidencia literal

## Capacidad implementada

`agora.traversal.walk` recorre unidades UTF-8 de una fuente fijada por SHA-256.
Cada llamada recibe la unidad y sus vecinas para reducir cortes de contexto.
El modelo extrae fragmentos literales; se conservan texto, hash y posiciones de
bytes verificables. Coincidencias repetidas en la misma posición se deduplican.
La búsqueda de posición conserva la primera coincidencia en cada ventana.

Se registran unidades, ventanas, respuestas, bytes de prompt, llamadas y evidencia
retenida. Hay presupuestos de llamadas, prompt por llamada, prompt acumulado y
texto retenido. Agotarlos produce recorrido parcial con rangos pendientes; no hay
reintentos, aumento automático de límites ni resumen generado. Un fragmento que
excede la capacidad de retención no se descarta silenciosamente: la unidad no se
marca procesada y se detiene el recorrido. Se verifica la revisión también al final.

Contrato nuevo: `agora/source-traversal/v0.1`. `traversal_status: full` significa
que todas las unidades tienen extracción de forma válida; no que todas las ideas
se conservaron. `semantic_coverage: unknown` y
`global_completeness: not_established` se mantienen incluso si todos los extractores
devuelven listas vacías. `execution_status: failed` invalida el cierre del recorrido,
aunque haya unidades procesadas antes del fallo. Los presupuestos de texto retenido
no incluyen el tamaño de los receipts; no son una cuota total de almacenamiento.

API independiente: no activa las CLI anteriores ni modifica el control de cobertura
global. El conjunto reducido de citas no se declara cobertura completa del original.
La revisión semántica y una respuesta global siguen siendo pasos posteriores.

## Ensayo GLM, 22 de septiembre de 2026

Fuente sintética congelada del ensayo anterior: 144 748 bytes, cuatro fases separadas
por relleno repetitivo. Pregunta global anterior, conocida por productor; no holdout.
Evidencia: `experiments/traversal-v1/runs/glm-01/`, ignorada por Git.

- 9 unidades de 16 384 bytes nominales, última menor; 9 llamadas, sin reintentos.
- Presupuestos: 9 llamadas, 524 288 bytes de prompt acumulado, 65 536 por llamada,
  16 384 bytes de citas retenidas; 2 048 tokens máximos de salida por llamada.
- Modelo solicitado y reportado: `glm-5.3-flash`; temperatura 0, timeout socket 90 s,
  límite externo del proceso 900 s. Credencial existente sólo en entorno.
- 15 archivos congelados verificados; anclajes de los cinco fragmentos comprobados
  contra la fuente. Resultado SHA-256:
  `cc964bda5a7367c8674f8ca5cc282c266a7f319dbf22453e77cae6eeed978f0e`.

| Elemento esperado | Resultado |
|---|---|
| Preparar almacén — Aina | Recuperado |
| Probar herramientas — Berto | Recuperado |
| Formar personal — Cora | Recuperado |
| Revisar resultados — Darío | Recuperado; antes omitido por búsqueda léxica |

También se retuvo un fragmento de 38 bytes sobre Eloy y el proyecto Risco,
irrelevante para Vela. La validación de literalidad no comprueba relevancia.
Conservamos ese resultado: no se eliminó para mejorar retrospectivamente la métrica.

Total: **95 090 tokens reportados**, **86,707 segundos**, **413 831 bytes de prompt**.
Se retuvieron cinco fragmentos, **323 bytes**, de los cuales **285 bytes** corresponden
a las cuatro fases. No se calculó coste monetario. Un resultado pequeño no equivale
a una lectura barata: se procesó todo y se repitió contexto por solapamiento.
No hay ahorro demostrado, comparación controlada de eficiencia ni nueva síntesis.

## Verificación y autorrevisión adversarial

**137 pruebas locales OK**, nueve nuevas: final de fuente, límites de llamadas,
prompt y retención, cita inventada, extracción vacía, cambio de revisión tras llamada,
fallo de proveedor sin reintento y anclajes exactos.

La autorrevisión identificó tres límites materiales: el modelo puede omitir algo
tras haber recibido una unidad; puede retener texto irrelevante; y el solapamiento
no garantiza conservar relaciones más largas que una ventana. El adaptador además
relee el original localmente en cada operación. No hubo revisión independiente.
No se declara exhaustividad general a partir de cuatro hechos sintéticos conocidos.

## Continuación recomendada

Construir un consumidor que muestre evidencia y estado parcial, y genere una
respuesta candidata sólo bajo un presupuesto explícito. Evaluar por separado
relevancia y fidelidad de esa respuesta, conservando visible la cobertura del recorrido.
Antes de optimizar llamadas, comparar ventanas y solapamientos en un corpus nuevo
con preguntas fijadas: recuperar la cuarta fase a este coste es evidencia funcional,
no un diseño de producción validado. El recorrido no tiene reanudación entre procesos.

Sin commit, push, memoria persistente ni modificaciones de AGENTS.md.

## Consumidor posterior

La [consulta explícita sobre el recorrido](consulta-recorrido.md) ya permite
una respuesta candidata conservando evidencia y pendientes. No certifica fidelidad.
