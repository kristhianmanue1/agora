# Cuestiones abiertas v2: perturbación del antecedente

Contrato experimental por campo: valor, soporte, requisitos faltantes, evidencia
literal y relaciones múltiples. El programa deriva estado (resolved/partial/open),
campos reabiertos y derivados afectados. Este cálculo depende del juicio del
modelo: no certifica verdad ni autoridad y no modifica documentos dependientes.

Cuatro casos nuevos: evaluación previa falsa, fuente antigua llegada tarde,
refutación sólo de fecha y cambio de fecha con asignación de responsable intacta.
Dos brazos: full sin evaluación previa; tracked con antecedente sembrado y falible.
Ambos reciben las mismas fuentes, corte temporal, requisitos y dependencias.
No es continuación generada por el modelo ni comparación directa con v1: es una
prueba de perturbación con antecedente controlado. No hay detección ni recuperación.

Máximo 8 solicitudes GLM glm-5.3-flash, temperatura 0, 8192 tokens de salida por
solicitud (65536 reservados), HTTP 90 s/proceso 100 s, sin reintentos. Casos, gold,
código, prompt y protocolo congelados antes de llamadas. Parada ante error de
transporte, consumo desconocido, formato inválido o congelación alterada.

Puntuación previa: valores, soporte, requisitos faltantes, estado calculado,
campos reabiertos y dependientes afectados. Las relaciones se inspeccionan
cualitativamente y no tienen un único gold de etiqueta. La evidencia se verifica
literalmente; soporte semántico requiere contraste separado. Una fecha errónea
arrastrada, sobreescritura por mera llegada, cierre falso o propagación a assignment
impide aceptar el caso. No modificar gold tras observar salidas.

Una ejecución, un autor de fixtures/gold/código: no revisión independiente,
benchmark externo ni holdout independiente. No se envían fuentes reales.
Reproduce: run.py <directorio_nuevo> con clave en entorno mediante Llavero.
