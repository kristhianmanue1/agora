# Cierre de la comparación de modo JSON

Fecha: 2026-09-23. Alcance completado: control de disponibilidad y seis pares
pendientes. Predecesor conservado: [campaña interrumpida](comparacion-modo-json.md).

## Decisión técnica

Mantener `--response-format default` y el perfil predeterminado `legacy`.
No promover `json_object`: no mostró beneficio en esta muestra y produjo una
respuesta que ni siquiera era JSON parseable. La opción sigue disponible,
desactivada por defecto. No se cambió el producto durante esta campaña.

## Método y evidencia

Ejecutor `experiments/provider-format-v1/run_remaining.py`; evaluación
`score_remaining.py`; resultados locales excluidos de Git en
`experiments/provider-format-v1/runs/paired-02`.

Se comprobó que el código actual coincidía con el congelado de `paired-01`.
Se congelaron protocolo, ejecutor, código y entradas antes de llamar al modelo.
Un control independiente ('Ada starts.') respondió correctamente con cita literal:
870 tokens y 3.723 segundos. Este control acredita respuesta en ese instante,
no disponibilidad futura.

Después se ejecutaron E3, E4, D2, D4, D6 y D8 en ambos modos. E3/default es una
nueva ejecución autorizada; el timeout anterior permanece intacto y su consumo
sigue siendo desconocido. No hubo reintentos dentro de esta campaña.
Modelo solicitado/reportado: `glm-5.3-flash`; endpoint Coding Plan de Z.ai;
perfil fijo `concise-v1`; temperatura 0; máximo de salida 8192 tokens;
timeouts socket/proceso de 90/110 segundos. Orden alternado por caso. Los
prompts y las fuentes fueron idénticos entre modos. Todos los casos son de
desarrollo previamente observados, no holdout ni evaluación QASPER.

| Seis pares nuevos | default | json_object |
|---|---:|---:|
| JSON parseable | 6/6 | 5/6 |
| Campos requeridos exactos | 6/6 | 5/6 |
| Contrato local aceptado | 6/6 | 5/6 |
| Respuestas aceptadas con estado esperado | 6/6 | 5/6 |
| Citas aceptadas verificadas contra bytes | 6/6 | 5/5 |
| Tokens reportados | 6551 | 8069 |
| Tiempo acumulado de solicitudes | 38.060 s | 55.359 s |

La campaña nueva completa (control más doce solicitudes) consumió **15490 tokens**
y 97.142 segundos acumulados. No hubo timeout nuevo.

Agregando los dos pares completos E1/E2 anteriores: default acepta 8/8 y JSON
7/8; 8655 frente a 10583 tokens (22.3% más en JSON). Es una agregación entre
campañas, no una ejecución simultánea ni evidencia estadística de superioridad.
El timeout anterior queda fuera de esos pares completos, pero **dentro del
registro operacional**: 18 intentos entre ambas campañas, contando el control;
20108 tokens conocidos más el consumo desconocido del timeout. No se permite
presentar 8/8 como fiabilidad de todos los intentos del modo predeterminado.

## Fallo observado

D4/json_object terminó con `stop`, entregó un objeto seguido de un párrafo
`Additional reading:`. Aunque el objeto inicial contiene una respuesta y citas
coherentes, el contenido completo no es JSON válido. Ágora lo rechazó con
`invalid_concise_answer_shape`. No se eliminó el párrafo ni se reparó la salida.
D4/default sí fue aceptado. No se atribuye una causa interna al proveedor; se
refuta la garantía de JSON válido para la combinación concreta probada.

## Autorrevisión semántica

- E3: ambos modos se abstienen; coordinar una instalación no identifica quién
  autorizó un pago que la fuente no menciona.
- E4: ambos se abstienen; 91% pertenece a Atlas, no a Boreal.
- D2: ambos conservan la afirmación explícita de revisión doble ciego.
- D4: default conserva mejora de asistencia en tres escuelas rurales. El texto
  de JSON conserva ese hecho, pero su entrega se rechaza y no cuenta como éxito.
- D6: ambos conservan el rechazo explícito de la compra, sin convertirlo en
  ausencia de información.
- D8: ambos mantienen 14 y 19 unidades, su atribución y la falta de precedencia.

Las once citas de respuestas aceptadas se verificaron por sus rangos UTF-8.
El número de citas difiere porque una salida agrupa frases y otra las separa;
no representa una diferencia de fidelidad. Las explicaciones también se
contrastaron con las fuentes. Revisión del productor, no independiente.

## Verificación y límites

Hashes de archivos congelados y respuestas verificados, incluyendo resultados
anteriores y control. Fuentes y código coinciden entre campañas. No se modificó
`src/` ni `tests/` en este bloque; la suite de 183 tests corresponde al mismo
código comprobado en el bloque anterior y no se repitió. Sintaxis de ejecutores
y evaluadores comprobada; `git diff --check` sin errores.

Muestra pequeña, casos conocidos, una respuesta por modo/caso, caché no
controlada. No se acredita ahorro de lectura, recuperación sobre fuentes grandes,
fidelidad general ni superioridad poblacional. El fallo de formato no justifica
promover otro modelo ni modificar los resultados QASPER previos.

## Próximo paso recomendado

Cerrar el ajuste de formato y volver al objetivo del producto: una prueba
acotada con una fuente grande, preguntas que unan secciones y una de visión
global, usando el modo y perfil predeterminados. Fijar antes de ejecutar los
hechos imprescindibles y sus pasajes; comparar lectura directa con recuperación
limitada, contando extracción, síntesis y llamadas fallidas. Medir omisiones,
respaldo de afirmaciones y coste total. No añadir otra variante de prompt o
formato en esa comparación. La integración con Skopos/AN-KLA sigue siendo
opcional y no resuelve por sí misma esos criterios.
