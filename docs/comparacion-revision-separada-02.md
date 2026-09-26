# Comparación combinada/separada — ejecución 02

**Completada, 2026-09-26.** Seis casos sintéticos, dos modalidades, 18 solicitudes
correctas, sin reintentos. Modelo solicitado y reportado: `glm-5.3-flash`.
Se conservó el intento 01 (HTTP 401) sin modificar sus artefactos.

## Acceso y procedencia

La credencial de ZAI_API_KEY heredada no coincidía con la guardada en el perfil
`zai` de Llavero. La ejecución 02 recibió la de Llavero mediante `ejecutar` y un
mapeo en memoria de SKOPOS_LLM_API_KEY a ZAI_API_KEY. Ambas rutas usaron el mismo
endpoint; el modelo del ensayo se fijó explícitamente y no se tomó del perfil.
La segunda credencial fue aceptada. No se editó el perfil, Keychain ni entorno
persistente, ni se imprimieron claves. No se conoce por qué la heredada falló.

## Resultados observados

| Métrica | Combinada v1 | Separada v1 |
|---|---:|---:|
| Casos completos | 6/6 | 6/6 |
| Respaldo correcto | 5/6 | 6/6 |
| Pertinencia correcta | 6/6 | 6/6 |
| Ambos ejes correctos | 5/6 | 6/6 |
| Pares íntegramente correctos | 2/3 | 3/3 |
| Solicitudes | 6 | 12 |
| Tokens totales reportados | 6640 | 5411 |
| Suma de duración por caso | 73.190 s | 64.594 s |

En el par de silencio, la cita dice que el informe no especifica qué llevaba
Maren; la afirmación dice que llevaba una llave de latón. La combinada responde
contradicted con la pregunta pertinente e insufficient con la pregunta ajena.
La separada mantiene insufficient en ambos. No saber qué llevaba no prueba que
no llevara una llave. Los pares de respaldo y negación explícita fueron correctos
en ambas modalidades.

Los tokens suman 12051, con cero consumos desconocidos en esta ejecución. No se
calculó coste monetario ni se verificó facturación. El intento 01 conserva su
propio consumo desconocido; no se suma como cero a esta ejecución.

## Evidencia y límites

`experiments/split-comparison-v1/result-glm-02.json` publica resultados por caso.
`score.py` recompone etiquetas desde respuestas preservadas y comprueba los
scores del ejecutor; `audit.py` verifica hashes. Los artefactos crudos siguen
locales e ignorados en `runs/glm-02/`: los resultados publicados no sustituyen
ese paquete completo. Casos, gold, código, protocolo y transporte se congelaron
antes de las llamadas. El scorer se añadió después, sin modificar las etiquetas
ni las respuestas; tiene controles contra casos ausentes, puntuación alterada,
gold alterado y ejecución aún abierta.

Autorrevisión adversarial, sin revisión independiente: son seis casos de control
con un sujeto y una afirmación, una ejecución por caso; no estiman exactitud de
producción ni significancia estadística. Los prompts difieren además de su
separación; no se atribuye causalidad exclusivamente a la arquitectura. El menor
consumo y duración aquí observados no garantizan ahorro: influyen contexto,
salida, comportamiento del modelo y caché. No hay comparación contra v3,
evaluación en español ni documentos largos. El idioma no tiene un gate simétrico
entre modalidades; las métricas comparadas son los dos ejes declarados.

## Recomendación

Conservar la vía separada como optativa, sin promoverla a predeterminada. La
siguiente batería debe añadir sujetos, atribución, incertidumbre, cifras,
excepciones y afirmaciones ambiguas, incluyendo español y casos nuevos fijados
antes de llamar. Medir también errores por detalle y omisiones; requerir mejora
repetida antes de elegir el modo por defecto. El experimento ya completado no
requiere otra llamada ni una ampliación automática de presupuesto.
