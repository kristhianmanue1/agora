# Ensayo de recuperación y suficiencia en fuente mayor

Un documento sintético con relleno repetitivo, no un corpus real ni prueba de escala
general. Tres preguntas: unión de dos secciones, coincidencias temáticas sin actor,
y visión global con cuatro fases separadas. Preguntas y referencia se fijan antes
de ejecutar; conocidas por el productor, sin cegamiento. No ajustar el prompt a ellas.

Comparación retrieve (top_k=3, presupuesto 2048 bytes) y reference (pasajes completos
indicados por el productor, control positivo, no recuperador automático). Ambos
procesos responden y evalúan en llamadas separadas, sin pasar el juicio a la respuesta.
La referencia no es baseline de lectura de fuente completa. No declarar ahorro neto.

Máximo 12 solicitudes, sin reintentos, glm-5.3-flash, temperatura 0, 2048 tokens de
salida por llamada, timeout socket 90s, deadline 110s por subprocess. Congelar fuente,
preguntas, código y runner antes de solicitar. Parar en timeout o dos fallos de
proveedor seguidos. Persistir rechazos de formato; no traducir enums a posteriori.
Ningún juicio autoriza buscar, responder, consolidar o admitir memoria: las dos
llamadas por ruta están prefijadas por el experimento, incluso si hay insuficiencia.

Revisar citas y explicaciones; contar por separado falsa suficiencia respecto al
original, omisión de hechos, abstención y rechazo estructural. La visión global puede
parecer suficiente si el juez desconoce una sección excluida: éste es un riesgo a
medir. Sumar uso de ambos modelos y tiempos; medir lectura local mediante instrumentación
del adaptador, además de bytes transmitidos. Mantener observación ante cualquier resultado.
