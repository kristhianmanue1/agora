# Relaciones candidatas con evidencia

CLI experimental, sin proveedores ni admisión automática. Entrada:
`agora/relation-candidate/v1`; salida: `agora/relation-assessment/v1`.

## Recorrido

Desde la raíz:

```sh
python3 scripts/agora_relations.py units --source /ruta/fuente.txt --source-id documento
python3 scripts/agora_relations.py template --source /ruta/fuente.txt --source-id documento > /tmp/relacion.json
# Completar textos e IDs en la plantilla.
python3 scripts/agora_relations.py validate --source /ruta/fuente.txt --source-id documento --candidate /tmp/relacion.json
```

Campos: `system`, `task`, `version`, `input`, `evaluation`. Cada uno contiene
`text` (texto o null) y `evidence_ids` (lista). `relation_evidence_ids` identifica
los pasajes propuestos para enlazar los campos. Una versión desconocida queda
como hueco; no se presume que la fuente publique una versión.

`units` reutiliza los IDs existentes ligados a fuente, SHA-256, offsets y texto.
La v1 admite una fuente y revisión por candidato. No extrae relaciones sola.

## Estados

- `needs_more_evidence`: faltan textos, referencias o evidencia de enlace.
  Es una carencia estructural del candidato, no ausencia probada en la fuente.
- `requires_semantic_review`: hay referencias para todos los campos y el enlace;
  falta comprobar que respaldan lo escrito.
- Siempre `semantic_support: not_verified` y `admitted: false`.

IDs ajenos o duplicados, fuente/revisión distinta, campos desconocidos y citas
con texto nulo se rechazan. Código de salida 0 significa estructura válida,
incluso con huecos; 2 indica rechazo. No implica aceptación semántica.
La salida conserva candidato, huecos y pasajes resueltos. No escribe memoria.

Límites: fuente UTF-8 de 4 MiB, candidato CLI de 1 MiB, 4.096 unidades y
32 referencias por campo/enlace. Unidades de hasta 4.096 bytes.

## Verificación y siguiente paso

Seis pruebas nuevas y regresión completa de 569 pruebas aprobadas (2026-10-03).
Incluyen recorrido CLI, identidad, UTF-8, huecos y una afirmación incorrecta con
ID válido que permanece sin verificar. Autorrevisión, no auditoría independiente.

Pendiente: conectar el generador y revisar cada relación contra sus pasajes.
El módulo no certifica significado, contradicción, exhaustividad ni identidad
semántica entre menciones.

## Generación y revisión conectadas

`agora_relation_run.py` añade dos operaciones separadas, sin modificar las tres
operaciones anteriores. Cada una admite una respuesta conservada (`--response`)
o un proveedor explícito (`--live`). No existe revisión ni reparación implícita.

```sh
python3 scripts/agora_relation_run.py generate --source /ruta/fuente.txt --source-id documento --expected-sha256 SHA --question 'Describe el sistema, entrada y evaluación' --live glm --out /ruta/nueva-generacion
python3 scripts/agora_relation_run.py review --source /ruta/fuente.txt --source-id documento --expected-sha256 SHA --candidate /ruta/nueva-generacion/candidate.json --live jev --out /ruta/nueva-revision
```

Sustituir SHA por el hash comprobado de la fuente. Para ejecución real, entregar
credenciales mediante Llavero al intérprete absoluto: GLM lee `ZAI_API_KEY` (o el
fallback ya definido por su transporte); Jev lee `TYPESAFE_API_KEY`. No guardar
secretos en argumentos ni archivos. Jev sólo revisa; GLM genera y también puede
revisar si se selecciona expresamente. Esta disponibilidad no decide cuál es
mejor revisor.

Para reproducir sin red, sustituir `--live` por `--response respuesta.json`, donde
el archivo contiene el objeto `response` conservado en un resultado anterior.
Se distingue `origin: supplied_response_replay` de `live_provider`.
`provider_calls` cuenta invocaciones del adaptador; en replay no son llamadas HTTP.

El directorio de salida debe ser nuevo. Antes de llamar al proveedor se guarda
un marcador `started`. `result.json` conserva prompt, respuesta, rechazo y
resultado estructural. `candidate.json` sólo se crea si la generación pasa la
validación estructural. Un marcador sin resultado final exige inspección; no
autoriza repetir automáticamente una llamada de resultado incierto.

El revisor recibe los campos y sus pasajes resueltos, más los pasajes del enlace.
Se registran los seis juicios y cualquier conflicto con huecos estructurales.
Sus etiquetas son opiniones conservadas: incluso `contradicted` no se convierte
en contradicción verificada. `admitted` permanece false y `semantic_support`
permanece `not_verified`. Todo resultado requiere revisión explícita.

Límites adicionales: prompt predeterminado de 200.000 bytes, una invocación por
operación, sin reintentos, 90 segundos por transporte y hasta 4.096 tokens de
salida GLM. No son garantías de coste ni equivalencias de tokens/bytes.

Prueba real sintética: GLM `glm-5.3-flash` generó y Jev `jev-1.13.0` revisó una
relación con seis juicios supported; sin admisión. GLM 1.511 tokens, Jev 3.133,
total observado 4.644; los reasoning tokens de GLM ya están incluidos.
Regresión completa: 576 pruebas aprobadas. La reproducción offline de ambas
operaciones también pasó. [Evidencia](../experiments/relation-flow-smoke-v1/README.md).
Esto valida conexión, no recuperación automática ni fiabilidad semántica general.
