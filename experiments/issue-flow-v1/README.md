# Flujo explícito: fuente nueva -> evaluación candidata

prepare(store, issue, expected_head, source, as_of) recupera la revisión indicada,
valida fuente/versión/corte y prepara un paquete sin red ni escritura. Rechaza
ID repetido o contenido idéntico a una fuente actual; esta política conservadora
no resuelve aliases o revisiones de fuente: usar identidad distinta por versión.
No descubre pendientes ni decide pertinencia de la nueva fuente.

evaluate_and_record verifica paquete y revisión antes de invocar al proveedor,
valida salida/consumo y añade candidato con compare-and-swap del padre. Una
actualización durante la llamada impide la escritura; la solicitud consumida no
se deshace. Guardado no significa admisión ni evaluación semántica independiente.
Un paquete modificado se contrasta con su reconstrucción desde el almacén, no
sólo con su propio hash. Hashes no autentican origen o autoridad.

Piloto: pendiente sintético de fecha con responsable Lina; nueva fuente confirma
fecha. Un GLM glm-5.3-flash, temperatura 0, máximo 8192 tokens de salida, timeout
HTTP 180 s/proceso 190 s, sin reintentos. Se conserva petición/respuesta incluso
si validación o escritura fallan. Inicialización manual declarada. Se verifica
fecha 2026-10-21 y Lina y recuperación exacta en proceso nuevo. No otra llamada
baseline: el contraste es contra las dos fuentes completas y expectativas fijas.

No red en preparación/tests. Una llamada real sólo mediante run.py <salida_nueva>
con credencial del entorno entregada por Llavero. Casos y código congelados antes.
No datos reales, watcher, sincronización ni integración Skopos/AN-KLA. Dependencias
experimentales: issue-store-v1 y open-issues-v3. Corridas ignoradas en Git.
