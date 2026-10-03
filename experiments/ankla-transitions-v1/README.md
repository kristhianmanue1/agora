# AN-KLA: supersede, checkpoints y bloqueo de comandos por attest

Prueba defensiva autorizada en stores sintéticos nuevos. Versión instalada
an-kla-memory 0.1.0b24. Ninguna escritura sobre memoria vigente, despliegue o servicio
de producción. Cero proveedores/LLM. No se modificó AN-KLA ni se ejecutaron pruebas
EKTEL. El bloqueo corresponde al mecanismo attest de AN-KLA, no a una integración
entre productos ni a una propiedad de MemOS.

## Propiedades y resultados

1. **Supersede:** escribir martes y sustituirlo por miércoles mediante plan-write →
   commit-write-plan. retrieve devolvió sólo schedule-v2 y excluyó schedule-v1 por
   inactivo. inventory de la revisión anterior conserva schedule-v1 y verify de esa
   revisión pasó. Falsaría la propiedad devolver el viejo como vigente o perder la
   revisión histórica. No se probó compactación ni recuperación tras corrupción.
2. **Checkpoint:** planificar/confirmar working-state-v2 con objetivo, fase y siguiente
   paso; checkpoint show coincidió con el estado suministrado y resume lo recuperó.
   Reutilizar el plan con revisión obsoleta fue rechazado con checkpoint_plan_base_changed;
   la revisión actual quedó idéntica antes/después. No se probó concurrencia multiproceso.
3. **Escritura obsoleta:** preparar un registro, avanzar la revisión mediante otra
   escritura y presentar el primer plan. write_plan_base_changed lo rechazó y la
   revisión vigente no cambió. No se afirma ausencia de logs u otros efectos diagnósticos.
4. **Acción real por attest:** un comando Python sólo intentaría crear marker.txt en
   el laboratorio. Con la whitelist predeterminada fue rechazado con
   attest_command_not_allowed y el archivo no existió. En otro store, una regla de
   argv exacto configurada antes del ensayo permitió el control positivo: el archivo
   se creó con «executed». Cambiar únicamente el destino a other-marker.txt produjo
   rechazo y ese segundo archivo no existió.

El control positivo demuestra que la acción podía ejecutarse en el entorno. La sonda
negativa no se explica por falta de permisos de escritura. La política sólo autoriza
ese argv exacto de laboratorio; no se debilitó una política de producción.

## Límite esencial del bloqueo

Esto demuestra rechazo antes de ejecución **a través de attest run**. No demuestra
que AN-KLA intercepte ejecuciones directas de un agente, sea un sandbox del sistema
operativo o resista a quien puede modificar su whitelist/clave local. Una frase
«no autorizado» en memoria tampoco modifica esa whitelist. La aplicación/harness
necesita imponer la ruta de ejecución si quiere hacer obligatorio el control.
No se desplegó tal integración ni se probó evasión por otra ruta.

## Errores del ensayo conservados

La primera vista full falló por no aportar subject exacto. La vista textual mostró
que los fixtures no tenían subject_ref; se verificó historia mediante inventory y
verify, sin inventar un sujeto. El primer captured_at no llevaba microsegundos y
falló la validación canónica. Se preparó otra entrada correcta. Ninguno de esos
fallos demuestra un defecto de producto ni obligó a repetir las escrituras iniciales.
Los archivos run.py/continue*.py conservan la secuencia de diagnóstico; no son el
punto de entrada para una reproducción nueva.

Después se ejecutó una reproducción limpia completa, que pasó todos los asserts.
result.json contiene resultados y hashes; runs/ y runs-replay/ guardan los stores
locales, claves y diagnósticos excluidos de Git. No publicar sus claves ni archivos
internos. No hubo revisión independiente.

## Reproducir en otro laboratorio NUEVO

```bash
.venv/bin/python -B experiments/ankla-transitions-v1/reproduce.py RUTA_NUEVA
```

El directorio no debe existir. El script crea registros y una whitelist exacta de
prueba sólo dentro de él, por lo que requiere autorización para ese laboratorio.
La salida debe indicar PASS; cualquier excepción impide declarar cierre exitoso.
La prueba está terminada: no implica cambiar defaults, instalar un control global
ni declarar resuelto el enforcement de todo ARIA.
