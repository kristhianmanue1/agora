# Comparación acotada: revisión combinada v1 / separada v1

Protocolo previo a ejecución. Seis casos sintéticos: tres pares de afirmación y
cita idénticas, con pregunta pertinente/ajena. Cubren respaldo, silencio y negación
explícita. Etiquetas esperadas independientes del payload. Idioma inglés.

Máximo 18 solicitudes a glm-5.3-flash, 8192 tokens de salida por solicitud,
147456 tokens de salida reservados; HTTP 90 s, proceso 100 s, sin reintentos.
Parada ante fallo de transporte o consumo desconocido. No ampliar límites ni
repetir una solicitud incierta. El total monetario depende de la tarifa de la
cuenta; los tokens de entrada se registran en usage, no son parte de esa reserva.
Sólo fixtures sintéticos, nunca documentos del Operador. Credencial desde entorno.

Se alterna qué modalidad va primero. La separada necesita dos llamadas y conserva
el orden respaldo→pertinencia. Se congela código, scripts, protocolo, casos y gold
antes de llamar. Se conservan solicitudes, respuestas finales, hashes, consumo,
modelo reportado y duración. No se conserva razonamiento interno ni credencial.

Criterios: acierto de respaldo, pertinencia y conjunto por caso; un par sólo tiene
éxito si ambos casos son correctos. Fallos de estructura y transporte cuentan en
cobertura, no se borran ni convierten en juicios semánticos. Comparar coste y tiempo
por caso completo; reportar consumos desconocidos por separado.

Comparación diagnóstica entre dos interfaces, no aislamiento causal de la
separación: sus prompts también difieren. No compara v3 ni acredita superioridad,
idioma español, documentos largos o generalización. Los resultados siguen siendo
juicios de GLM y no adjudicación automática de candidatos.

Ejecutar con ZAI_API_KEY en entorno y un directorio nuevo bajo runs/:
`PYTHONDONTWRITEBYTECODE=1 python3 experiments/split-comparison-v1/run.py experiments/split-comparison-v1/runs/glm-01`
