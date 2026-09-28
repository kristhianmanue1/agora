# Contrato experimental v4: citas y alcance suministrado

Corrección del rechazo `missing_evidence` observado en partial-selection-v2.
Nueva envoltura explícita `agora/issue-assessment/v4-experimental`: schema,
fields, reason y reviewed_scope. Los campos del modelo mantienen su forma.

- `missing` permite evidence vacía; sigue exigiendo valor null y requisitos faltantes.
- `supported`, `disputed` y `withdrawn` siguen exigiendo citas literales no vacías.
- El host construye reviewed_scope desde la entrada exacta: identidad y hash de
  fuente; revisión, localizadores y offsets UTF-8 del paquete cuando existen.
- `basis=supplied_input_only`: documenta lo entregado para evaluación. **No acredita
  que el modelo leyó cada fragmento ni que buscó exhaustivamente.** No prueba
  ausencia global, autenticidad del original ni frescura frente a Skopos.
- Para paquetes, las citas sólo pueden proceder del texto de un segmento
  seleccionado, nunca de metadatos o de una unión artificial entre segmentos.
- El validador exige coincidencia exacta de alcance con la entrada; rechaza
  identidades, versiones, localizadores, límites o declaraciones cambiados.

`prepare_candidate(content, data)` añade explícitamente la envoltura del host;
no modifica campos o razón del modelo. `validate` exige v4 y no migra v3 de forma
implícita. El replay conserva hash de la respuesta original y de la nueva
representación, y declara quién añadió alcance/esquema.

Los consumidores SQLite/recovery actuales permanecen fijados a v3. No se cambia
su historial, su hash de validador ni su interpretación. La adopción en un flujo
nuevo requiere compatibilidad y persistencia explícitas; todavía no está activada.

La validez estructural no prueba respaldo semántico: dos citas pueden concordar
en vez de contradecirse, y reason aún puede formular afirmaciones indebidas.
La revisión de fidelidad permanece necesaria. Contrato experimental, no admisión.
