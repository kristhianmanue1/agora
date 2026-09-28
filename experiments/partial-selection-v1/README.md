# Lectura parcial y ampliación — piloto v1

Dos llamadas GLM 5.3 Flash como máximo, sin reintentos, 8192 tokens de salida y
180 segundos HTTP por llamada. Sólo una reunión sintética; sin fuentes reales.

La primera selección conserva responsable pero omite una fecha que sí existe en
otro segmento de la misma revisión. Debe quedar parcial, sin afirmar ausencia en
toda la reunión. La segunda selección incluye ambos segmentos: debe resolver la
fecha y conservar responsable. Es el control positivo de recuperación.
Las expectativas y los hashes de código se guardan antes de la primera llamada.

Se reutilizan el exportador experimental de Skopos, el sobre autocontenido y la
recuperación SQLite. La configuración del módulo aislado incorpora el texto y
hash del prompt de sistema al request persistido; no cambia la API histórica ni
promete controlar proveedores externos. Cada operación guarda el prompt real.

La comprobación estructural y de valores es automática. El alcance de las
negaciones y la fidelidad de citas requieren autorrevisión del resultado real.
Dos selecciones del mismo origen no constituyen corroboración independiente.
No mide ahorro, no compara modelos, no acredita robustez general ni admite
resultados en AN-KLA. Las fechas futuras son datos sintéticos.

Ejecución: `run.py RUTA_NUEVA`, con ZAI_API_KEY inyectada por Llavero. Los runs
locales guardan requests, respuestas, paquetes y SQLite; no contienen la clave.
