# Base experimental Ágora–SKEVI v1

Esta carpeta materializa el controlador neutral de
`agora-skevi-experiment/v1`. Verifica el freeze, prepara manifests y contiene el
runner mecánico M1. No implementa la vertical slice, no instala SKEVI y no
incluye un adaptador de agente, reviewer semántico ni fixtures ejecutables.

## Componentes

- `experiment.lock.json`: proyección ejecutable del contrato documental
  congelado. Los Markdown y la revisión Git indicada conservan la autoridad que
  les asigna la matriz del proyecto.
- `schemas/run-manifest.schema.json`: forma cerrada de una corrida preparada.
- `scripts/verify_freeze.py`: recalcula digests de archivos y secciones.
- `scripts/prepare_run.py`: crea un run manifest fuera del repositorio después
  de verificar el freeze. No inicia la corrida.
- `scripts/runner.py`: ejecuta un adaptador explícito dentro de un workspace
  Seatbelt, captura evidencia y prepara un paquete de reviewer sin condición.
- `scripts/isolation.py`: ambiente mínimo, filesystem acotado y red denegada.
- `tests/`: verifica integridad, asignación C0/C1 y fail-closed.

## Verificación

```bash
python3 experiments/agora-skevi-v1/scripts/verify_freeze.py
python3 -m unittest discover -s experiments/agora-skevi-v1/tests -v
```

La integración de Seatbelt requiere ejecutarse fuera de otro sandbox:

```bash
AGORA_ISOLATION_INTEGRATION=1 \
  python3 -m unittest discover -s experiments/agora-skevi-v1/tests -v
```

Preparar un manifest requiere un `agora_base_commit` ya construido y un destino
externo nuevo:

```bash
python3 experiments/agora-skevi-v1/scripts/prepare_run.py \
  --run-id <id> --pair-id <1..3> --slot-id <1|2> \
  --base-commit 47fb709358a626a8f9c1d35ab442eecfe8a20f41 \
  --output /ruta-aislada/run.json
```

El comando sólo prepara datos. `runner.py` no debe usarse con un productor real
hasta congelar M2 y recibir autorización de ejecución. Las pruebas usan un
productor falso sin llamadas de modelo.

## Evidence bundle M1

```text
run/
├── run-manifest.json
├── input/
├── producer/
│   ├── artifacts/
│   ├── patch.diff
│   ├── execution-record.json
│   ├── runner-record.json
│   ├── stdout.log
│   └── stderr.log
├── tests/results.json
├── reviewer/
│   ├── input/
│   └── review.json
└── integrity/digests.json
```

El runner sólo registra integridad, presupuesto, aislamiento y señales
mecánicas. `semantic_verdict` permanece `not_evaluated`; el reviewer o los
verificadores externos deciden arquitectura y correctitud.

El paquete de reviewer omite manifest, condición e instruction packs. M1 no
afirma cegamiento completo: los propios artefactos podrían revelar la metodología
y M2 deberá medir y registrar esa inferencia.

La base productora M1 es una proyección vacía identificada por
`agora-producer-empty-base/v1`. Se deriva del commit fijado, pero no expone su
árbol, `.git` ni documentos: ambos brazos empiezan desde el mismo workspace vacío
y reciben los instruction packs autorizados fuera de banda. M3 deberá versionar
la proyección si el workload necesita archivos iniciales.
