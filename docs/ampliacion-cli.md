# Ampliación de evidencia desde la CLI

Los comandos nuevos pertenecen a `python -m agora.issue_cli`. Requieren el checkout
completo. Reutilizan búsqueda y contratos de proveedor ya probados, sin cambiar
pendientes v4, las bases anteriores ni los revisores predeterminados.

`review-init` crea explícitamente `reviews.sqlite3` en un workspace existente.
Es un registro separado de juicios sobre afirmaciones, no una migración del historial
de pendientes. No existe un head único: pueden compararse derivados GLM y Jev del
mismo padre. Una revisión nueva no supersede ni admite automáticamente la anterior.

## Recorrido sin API

Desde la raíz del repositorio, copiar en bash o zsh. Sólo usa fixtures sintéticos.
El primer juicio es deliberadamente incorrecto y simulado; no proviene de GLM real.

```bash
export PYTHONPATH="$PWD/src"
export PYTHONDONTWRITEBYTECODE=1
agora_trial=$(mktemp -d)
function agora_review() { python3 scripts/agora_issues.py --workspace "$agora_trial/workspace" "$@"; }
agora_review init
agora_review review-init
agora_review review-import --review original --input examples/review-expansion/initial.json
agora_parent=$(agora_review review-inspect --review original | python3 -c 'import json,sys; print(json.load(sys.stdin)["sha256"])')
agora_source=$(python3 -c 'import hashlib; print(hashlib.sha256(open("examples/review-expansion/source.txt","rb").read()).hexdigest())')
agora_review expand-prepare --parent original --expected-parent "$agora_parent" --source examples/review-expansion/source.txt --source-id demo-engine --source-sha256 "$agora_source" --budget 4096 --out "$agora_trial/plan.json"
agora_plan=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["sha256"])' "$agora_trial/plan.json")
agora_review expand-inspect --plan "$agora_trial/plan.json" --expected-plan-sha256 "$agora_plan" --details
```

Inspeccionar el paquete antes de evaluar: conserva pregunta, afirmación, evidencia
anterior, pasajes, localizadores, consulta y revisión de fuente. Preparar no cambia
el juicio anterior. `--budget` limita texto recuperado; la evidencia anterior y el
JSON añaden bytes. La búsqueda lee la fuente completa localmente.

```bash
agora_review expand-evaluate --review glm-replay --plan "$agora_trial/plan.json" --expected-plan-sha256 "$agora_plan" --provider glm --response examples/review-expansion/glm-response.json
agora_review expand-evaluate --review jev-replay --plan "$agora_trial/plan.json" --expected-plan-sha256 "$agora_plan" --provider jev --response examples/review-expansion/jev-response.json
agora_review review-inspect --review original
agora_review review-inspect --review glm-replay --details
agora_review review-recover --operation glm-replay
```

El original sigue `supported`; los derivados son `contradicted`, vinculados al hash
del original y del plan, `supplied_response_replay`, `not_admitted`. No son nuevas
respuestas reales de proveedor. `--details` muestra contenido: usarlo sólo donde
sea apropiado exponer las fuentes. Los archivos y bases se crean privados mediante
la CLI; los hashes detectan correspondencia, no autenticidad ni autoridad.

## Llamada real opcional

Elegir un id nuevo para una llamada nueva y usar `--live` en lugar de `--response`.
GLM recibe ZAI_API_KEY o SKOPOS_LLM_API_KEY; Jev recibe TYPESAFE_API_KEY.
Llavero puede inyectarlas; no escribirlas en archivos ni argumentos.
El punto de entrada scripts/agora_issues.py resuelve src desde el checkout y funciona
sin PYTHONPATH, que Llavero retira del entorno del proceso ejecutado.

Ejemplo GLM, después de inspeccionar el mismo plan:

```bash
python3 /Users/krisnova/www/aria/llavero/llavero.py ejecutar zai -- python3 scripts/agora_issues.py --workspace "$agora_trial/workspace" expand-evaluate --review glm-live --plan "$agora_trial/plan.json" --expected-plan-sha256 "$agora_plan" --provider glm --live
```

Para Jev usar perfil `agora.dev.typesafe`, `--provider jev` e id diferente.
La llamada envía la evidencia al proveedor: glm-5.3-flash con máximo 2048 tokens
de salida y temperatura 0, o jev-1.13.0 con choice; 90 segundos, sin reintentos.
El paquete no lleva un límite monetario. La validación inicial usó respuestas conservadas. La comprobación real posterior
de este transporte está registrada al final de esta guía.

## Fallos y recuperación

- Antes del envío se revalida el plan contra el padre, la fuente y el recuperador.
  Fuente cambiada, padre distinto, plan alterado o clave ausente: rechazo sin envío.
- La operación se reserva antes de llamar. Si no llega una respuesta guardada,
  `attempted` significa resultado incierto. Repetir el mismo id no vuelve a enviarla.
  Un id nuevo sí puede duplicar consumo: no es recuperación.
- La salida original se conserva como `response_ready` antes de analizarla.
  Una salida inválida permanece ahí y se rechaza; no se repara automáticamente.
- Juicio derivado y operación `committed` se guardan en una transacción. Un fallo
  revierte ambos cambios, conservando la respuesta guardada para recuperar.
- `review-recover` nunca llama al proveedor y trabaja con el paquete guardado;
  no exige que la fuente actual siga disponible. Esto recupera historia, no certifica
  que siga vigente. Reutilizar un id con otro plan/proveedor/respuesta se rechaza.
- `review-init` rechaza una base existente; si falla su creación puede dejar una
  base incompleta. No hay migración ni reparación automática de esa base.

No hay disparo por confianza, vigilancia automática, adjudicación ni admisión en
AN-KLA. La selección puede ser insuficiente aunque devuelva pasajes; cero resultados
no prueba que no exista evidencia. `expand-inspect` informa suficiencia desconocida.

## Verificación del incremento — 2026-09-28

441 tests pasan, incluidos nueve nuevos de extremo a extremo y fallos de persistencia.
Los dos bloques locales de esta guía se ejecutaron juntos sin editar scripts.
Se conservaron los juicios originales, se crearon derivados GLM/Jev reproducidos
y se recuperó la revisión sin llamada al proveedor. Cero llamadas nuevas.
Autorrevisión del diff y comportamiento; no hubo revisión independiente.

## Validación real posterior — 2026-09-28

La primera ejecución mediante Llavero falló antes de reservar operación: el entorno
saneado retiró PYTHONPATH y Python no encontró agora. Se añadió el punto de entrada
scripts/agora_issues.py y se probó desde otro directorio, sin PYTHONPATH y con -I.
No se modificó Llavero ni su política de entorno.

Después se ejecutó una llamada por proveedor con el mismo plan sintético. Ambos
reportaron contradicted, origin=live_provider, admission=not_admitted. Modelos
solicitados y reportados: glm-5.3-flash y jev-1.13.0. GLM reportó 244 tokens de
entrada y 102 de salida (346 total), Jev 450 y 47 (497 total). Duración del comando
completo, incluyendo Llavero y proceso: 3.487 s y 0.432 s. No se verificó coste monetario.

La recuperación en procesos nuevos sin credenciales devolvió el mismo hash para
cada derivado. Original y fuente sin cambios. Dos llamadas nuevas, cero reintentos
de proveedor. 442 tests pasan. Esta comprobación acredita funcionamiento de la
ruta real con ese caso; no generaliza fidelidad ni estabilidad de los revisores.
Autorrevisión, sin revisión independiente. El generador y el revisor predeterminado
no cambiaron; no hubo admisión en memoria.

[Evidencia: plan, originales, operaciones, respuestas y recuperación](evidence/ampliacion-cli-live-2026-09-28.json).
El SHA base del registro precede al nuevo lanzador; los hashes de código identifican
los archivos realmente probados, incluidos los cambios aún sin commit al ejecutar.

Siguiente paso: usar esta interfaz con casos nuevos reservados y preguntas globales,
midiendo información omitida además del respaldo de afirmaciones. La validación
de transporte ya no es el cuello de botella de este recorrido.
