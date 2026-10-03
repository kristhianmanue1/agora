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
