# Comparación combinada/separada — intento 01

**PARCIAL, 2026-09-26:** la primera solicitud a GLM devolvió HTTP 401 en
0.418 segundos. Se detuvo el ensayo sin reintentos ni cambios de presupuesto.
La presencia de ZAI_API_KEY en el entorno no acredita una credencial aceptada.
El código HTTP indica rechazo de autenticación; no determina su causa concreta.

Protocolo: seis casos, tres pares de respaldo/silencio/negación con pregunta
pertinente o ajena, comparando revisión combinada v1 con separada v1. Máximo 18
solicitudes, 8192 tokens de salida por llamada, 90 s de HTTP, sin reintentos.
Detalles en `experiments/split-comparison-v1/README.md`.

Resultado: una solicitud intentada, cero respuestas evaluables, cero casos o pares
comparables. La modalidad separada no llegó a ejecutarse. No hay medida de acierto,
mejora, ahorro ni coste total. Tokens conocidos: 0; una solicitud sin telemetría
de consumo. Ese subtotal no significa consumo total cero.

Los scripts y protocolo quedan publicados; los artefactos de la ejecución local
se conservan ignorados por Git en `experiments/split-comparison-v1/runs/glm-01/`.
La auditoría local verificó el manifiesto congelado y hashes de solicitud,
respuesta de error y resultado. Los hashes acreditan integridad local, no autoría
externa ni que una respuesta ausente fuera correcta.

Para retomar: corregir o sustituir la credencial GLM por el mecanismo local de
credenciales, sin pegar secretos en el chat. Abrir una ejecución nueva con
presupuesto explícito, conservar intacto el intento 01 y comparar ambas modalidades.
No reintentar automáticamente ni incorporar este fallo como acierto semántico.
