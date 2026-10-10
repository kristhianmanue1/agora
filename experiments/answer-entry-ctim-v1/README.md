# Entrada `answer` con GLM y revisión Jev: CTIM 18–22

**Fecha:** 2026-10-10. **Alcance:** una fuente UTF-8 de 1.300 bytes,
transcripción manual cotejada de la página física 15 del procedimiento
`2900-003-001`. No se usó la API de página Skopos ni se demostró vínculo
automático al PDF original o su vigencia. Los archivos de `runs/` conservan
las respuestas y recibos de esta ejecución.

`scripts/agora.py run answer` recibió la fuente SHA-256
`db72e2fbb43e100102e39beb1d11a5b09eaafb8df76f2c3c8fbc06c6f131ea66`,
la pregunta congelada en `ctim-sequence-completeness-v1/freeze.json` y
`requirements.json`. La primera invocación no encontró el directorio padre de
salida y falló **antes de reservar un intento o llamar al proveedor**. Se creó
ese directorio y se hizo una sola ejecución real con Llavero `zai` y modelo
solicitado `glm-5.3-flash`, sin reintentos del proveedor.

La ejecución completó cinco despachos: generación, respaldo, pertinencia,
cobertura y diagnóstico. Produjo cinco afirmaciones en orden 18–22;
responsables CPIM para 18 y CTIM para 19–22. Las cinco recibieron respaldo y
pertinencia `supported/relevant` de GLM. La revisión global devolvió
`complete` y el diagnóstico `no_omission_found`. Los recibos reportan 15.612
tokens totales en conjunto y modelo `glm-5.3-flash`; no acreditan factura ni
identidad efectiva del ejecutor.

`scripts/agora.py run jev-review` recibió el candidato ya guardado, sin volver
a llamar GLM. Una llamada Jev solicitó `jev-1.13.0` mediante Llavero
`agora.dev.typesafe` y devolvió cinco etiquetas `supported`, una por
afirmación, con 2.214 tokens de entrada y 223 de salida reportados. Jev sólo
evaluó las citas adjuntas; no revisó cobertura del documento completo.

`scripts/agora.py run export-answer` creó offline un
`agora/consultation-package/v1-experimental` con cinco afirmaciones, citas,
rangos, etiquetas separadas y hashes. Su SHA-256 es
`34cbeaef301b01ee077044f053fa0947c73ced241de2e86a57fdf334cc4bf985`.
El paquete conserva `original_integrity=not_established` y
`disposition=requires_review`; **no es una cita lista para el gate de
expertoGobernanza**.

El auditor offline comprueba hashes, etapas, cinco intentos/respuestas,
secuencia y actores, literal de citas, enlace Jev y alcance del paquete:

```sh
.venv/bin/python experiments/answer-entry-ctim-v1/audit.py
```

La concordancia de modelos en una pregunta conocida no reemplaza evaluación
reservada, revisión visual del PDF ni el preflight del consumidor. El contrato
bilateral para entregar citas con página y `item_id` exige un derivado Skopos
verificado y una prueba separada de su adaptador v0.2.
