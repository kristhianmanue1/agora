# Fragmentos de cita de 1.000 bytes: resultado negativo

Con el mismo QASPER `1911.10401`, pregunta y límites, se cambió únicamente el tamaño
máximo de unidad de 4.096 a 1.000 bytes. Se leyó toda la fuente. Las 59 unidades
conservan el contenido no blanco y sus localizadores UTF-8.

Con hasta 12 usos de citas, unidades de hasta 1.000 bytes acotan la suma a 12.000.
La propiedad aritmética no garantiza que el modelo cumpla el máximo de usos ni
que las unidades divididas sean suficientes semánticamente.

**Resultado:** `finish_reason: length`, contenido vacío. El proveedor registró los
4.096 tokens de salida como razonamiento. El candidato quedó rechazado mediante
`generation_incomplete`; ninguna revisión ni reparación. Una llamada, 13.427 tokens,
64,096 segundos. No se modifica el default y no se interpreta como evidencia de
cobertura o ahorro. Tampoco se atribuye causalmente el fallo a la partición: una
sola ejecución y comportamiento no determinista no permiten hacerlo.

`verify.py` reproduce el rechazo con la respuesta conservada y comprueba hashes,
localizadores y contenido, sin red. Los artefactos completos están en directorios
ignorados y el resultado resumido conserva la respuesta y hashes.

La alternativa se probó en [agrupación de citas](../citation-grouping-v1/README.md),
una condición distinta con fragmentos originales y sin aumentar tokens.
