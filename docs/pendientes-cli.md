# CLI experimental de pendientes

Una entrada reúne preparación, evaluación, inspección, recuperación y reparación:
`python -m agora.issue_cli`. Requiere Python 3.10+ y el checkout completo de Ágora;
no es aún un paquete instalable independiente. Reutiliza los contratos congelados
issue-flow-v4 y repair-store-v1. No mueve sus implementaciones ni migra bases antiguas.
Las otras CLI de consulta y transformación conservan su interfaz.

## Recorrido local sin API

Desde la raíz del repositorio, copiar estos comandos en bash o zsh. Se crean
archivos privados en un directorio temporal; las fuentes son sintéticas.
No hay que editar scripts ni acceder a carpetas internas de experimentos.

```bash
export PYTHONPATH="$PWD/src"
export PYTHONDONTWRITEBYTECODE=1
agora_trial=$(mktemp -d)
function agora_issue() { python3 -m agora.issue_cli --workspace "$agora_trial/workspace" "$@"; }
agora_issue init
agora_issue seed --issue nube --input examples/issues-v4/initial-input.json --response examples/issues-v4/initial-response.json
agora_head=$(agora_issue inspect --issue nube | python3 -c 'import json,sys; print(json.load(sys.stdin)["head"])')
agora_issue prepare --issue nube --expected-head "$agora_head" --source examples/issues-v4/new-source.json --as-of 2026-10-09 --out "$agora_trial/prepared.json"
agora_issue evaluate --operation formato-01 --prepared "$agora_trial/prepared.json" --response examples/issues-v4/response-format-error.json
agora_issue inspect --operation formato-01
agora_issue recover --operation formato-01
```

`evaluate` y `recover` terminan aquí con código 2: el ejemplo conserva una respuesta
histórica con un backtick sobrante. Es un rechazo esperado, no una llamada nueva.
La operación queda `response_ready`; el historial mantiene su única revisión.
`inspect --operation formato-01 --details` permite consultar la respuesta original.
La respuesta inicial es una grabación histórica suministrada, no una ejecución
verificada por esta CLI. Las fechas futuras forman parte del caso sintético.

## Reparación deliberada, con original conservado

```bash
agora_issue repair-propose --operation formato-01 --expected-head "$agora_head" --out "$agora_trial/repair.json"
agora_plan=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["sha256"])' "$agora_trial/repair.json")
cat "$agora_trial/repair.json"
agora_issue repair-apply --derivation formato-01-repair --plan "$agora_trial/repair.json" --expected-plan-sha256 "$agora_plan"
agora_issue inspect --derivation formato-01-repair
agora_issue inspect --issue nube
```

Revisar el plan antes de aplicarlo. La política sólo admite quitar un único backtick
final; no permite reescribir valores, citas o explicaciones. El resultado es un
`host_format_repair`, `not_admitted`, en un registro separado. El original sigue
rechazado y no aparece una segunda revisión en su historial. Repetir la aplicación
con igual identificador y contenido devuelve el mismo derivado si el origen sigue
vigente. Un cambio de cabecera obliga a revisar y preparar de nuevo.

Para probar el camino válido en ese mismo workspace:

```bash
agora_issue evaluate --operation correcto-01 --prepared "$agora_trial/prepared.json" --response examples/issues-v4/response-simulated.json
agora_issue recover --operation correcto-01
agora_issue inspect --issue nube
```

Ahora hay dos revisiones; el resultado declara `supplied_response_replay`.
No demuestra que un proveedor produzca esa respuesta ni que haya leído toda la fuente.

## Ejecución real y límites

`evaluate --live` sustituye a `--response`; requiere `ZAI_API_KEY` inyectada mediante
Llavero, nunca escrita en argumentos ni archivos. Configuración actual congelada:
`glm-5.3-flash`, temperatura 0, máximo 8192 tokens de salida, 180 segundos de HTTP
(190 para el subproceso). No es un límite de tokens totales ni monetario.
La llamada transmite el paquete preparado al proveedor. Usar otro workspace y
preparación para la prueba real, sin reutilizar una operación ya reproducida.

Conservar el identificador de operación: una respuesta guardada se recupera sin
otra llamada. Si hubo envío pero no hay respuesta guardada, el estado es incierto;
no se reenvía automáticamente. Usar un identificador nuevo podría duplicar consumo.
`recover` nunca llama a un proveedor. Un `committed` es persistencia local, no
admisión en memoria ni validación semántica. `resolved` sólo describe el resultado
del contrato sobre la evidencia suministrada.

`init` exige un directorio inexistente cuyo padre ya exista. Si falla a mitad,
puede dejar un directorio incompleto: conservarlo para diagnóstico y elegir otro;
no hay transacción conjunta para crear ambas bases. Los planes incluyen fuentes y
respuestas: tratarlos con la misma confidencialidad que los originales. Los hashes
comprueban correspondencia, no autenticidad ni autorización humana.

## Verificación de este incremento

`tests/test_issue_cli.py` ejecuta comandos en procesos nuevos, con respuestas
conservadas y simuladas. Cubre recorrido válido, rechazo y reparación, repetición,
conflicto de respuesta, ausencia de credencial y prohibición de sobrescritura.
No se ejecutaron llamadas nuevas a GLM ni Jev para esta consolidación.
La prueba real acotada y la evaluación comparativa de Jev son pasos posteriores.

Comprobación del 2026-09-28: 421 tests pasan (6 de la nueva CLI). Los tres
bloques de comandos de esta guía se ejecutaron juntos en bash: rechazo esperado,
derivado separado, original con una revisión y replay válido con dos revisiones.
Autorrevisión del incremento; no se realizó revisión independiente.

Ampliación explícita de juicios sobre afirmaciones: [guía y comandos](ampliacion-cli.md). Usa un registro separado creado con review-init.
