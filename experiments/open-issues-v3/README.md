# Pendientes v3: forma explícita y revisión de dependencias versionadas

Dos casos de v2: refutación parcial y cambio de fecha con responsable intacto.
Fuentes textuales y expectativas de valores/estado intactas. Nuevo prompt con
tipo explícito y ejemplo neutral; añade change_source_ids por campo. Se conservan
citas y relations como cadenas, sin normalizar respuestas incompatibles.

Cada dependiente declara basis y reviewed_sources con identidad y SHA-256.
La fuente se verifica contra su hash. IDs duplicados, versiones distintas y
snapshots incompletos se rechazan. Si un cambio relevante ya fue revisado por
el dependiente, no se vuelve a señalar por ese mismo cambio. Se añade un control
already_reviewed_schedule; schedule usa la versión previa y assignment sólo owner.

`affected` significa candidato a revisión por cambio relevante no revisado,
NO documento falso ni invalidación automática. Los snapshots son declarados en
fixtures, no recibos de revisión autenticados. La corrección semántica de relaciones
y change_source_ids sigue dependiendo del modelo; hashes no prueban esa corrección.
No se afirma propagación transitiva, concurrencia, permisos ni motor persistente.

Máximo cuatro llamadas a glm-5.3-flash, temperatura 0, 8192 tokens de salida por
llamada, timeout HTTP 180 s/proceso 190 s, sin reintentos. Parada ante fallo de
transporte, formato, consumo desconocido o alteración de congelación. Dos brazos:
full sin antecedente y tracked con antecedente sembrado de v2; mismas fuentes.

Gold fijado antes de llamadas. Se puntúan valores, soporte, requisitos, estado,
campos reabiertos y candidatos afectados. Citas literales verificadas; juicio
semántico revisado por el productor, sin independencia. Éxito requiere conservar
Lina, retirar sólo fecha en refutación, actualizar fecha en cambio, señalar sólo
schedule y no señalar assignment ni already_reviewed_schedule. Rechazos conservados.

No es comparación causal con v2: cambian prompt y metadatos de dependencias.
No hay datos reales, incorporación de memoria ni publicación automática.
