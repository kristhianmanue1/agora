# Batería ampliada, protocolo previo

Doce casos nuevos, seis pares con pregunta pertinente/ajena: fecha, sujeto,
atribución sin verificar, excepción, incertidumbre y suma de dos fragmentos.
Tres pares en español y tres en inglés. Casos y gold fijados antes de llamar;
las etiquetas nunca se envían al proveedor. El caso de fecha niega explícitamente la entrega del día 12; no se deduce
una contradicción sólo por observar otra fecha. La batería evalúa afirmaciones dadas, no omisiones
de generación. Esa cobertura se observa por separado en el piloto integrado.

Comparada v1 / separada v1, sin cambiar prompts. Máximo 36 solicitudes GLM,
8192 tokens de salida por llamada, reserva 294912; HTTP 90 s/proceso 100 s.
Sin reintentos; detener ante transporte/acceso fallido o consumo desconocido.
Clave desde Llavero, modelo explícito glm-5.3-flash. Alternar orden de modalidades.
Una ejecución, sin potencia estadística ni causalidad arquitectónica acreditadas.

Métricas y auditoría: mismas que v1, recomputadas desde respuestas, con conteos
por eje, caso, par, idioma, tokens y duración; casos no ejecutados quedan visibles.
Promover a predeterminado requiere más evidencia. No hay aprobación automática.
