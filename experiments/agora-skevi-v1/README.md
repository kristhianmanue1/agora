# Base experimental Ágora–SKEVI v1

Esta carpeta materializa el controlador neutral de
`agora-skevi-experiment/v1`. Verifica el freeze, prepara manifests y contiene el
runner mecánico M1-R1. No implementa la vertical slice, no instala SKEVI y no
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

M1-R1 corrige defectos encontrados por la ronda adversarial posterior a M1:
ancla la identidad completa del freeze, valida los campos de ciclo de vida del
manifest, evita seguir symlinks del adaptador, rechaza objetos especiales y
limita la duplicación de artefactos a 10 000 archivos y 64 MiB. También evita
clasificar un outcome negativo como invalidez del protocolo y restringe la
visibilidad de metadatos y procesos. Las anomalías posteriores al lanzamiento
se sellan como `invalidity_candidate` en vez de borrar su evidencia. Si el
propio sellado falla, el staging se conserva como evidencia no sellada y se
reporta mediante `recovery_staging`; nunca se presenta como bundle válido. La
finalización no reemplaza un destino existente y el runner registra el commit,
estado dirty y digests de sus componentes; si Git no está disponible, esa
identidad se marca `unavailable` sin impedir la preservación.

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

Seatbelt reduce acceso a red, repositorio, otros runs y secretos heredados, pero
M1-R1 no demuestra contención hermética de código hostil. En particular, no hay
cuota de filesystem durante la ejecución ni garantía probada contra procesos
que se desacoplen del grupo antes de la finalización. Resolver estas dos
limitaciones es un gate de M2 antes de cualquier corrida real.

Las métricas de modelo, tokens e invocaciones de M1-R1 proceden del propio
productor: son `unverified_self_report` y no constituyen enforcement de
presupuesto ni prueba de identidad. M2 debe obtener receipts observados por el
host. También debe incorporar un ledger que impida preparar selectivamente
manifests ilimitados para la misma pareja/slot antes de ejecutar el piloto.

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

## Gate adversarial

SKEVI exige una ronda adversarial fresca sobre cada resultado material al que
se aplique el perfil. El artefacto de revisión debe identificar la versión
revisada, hallazgos, correcciones, riesgos residuales, ejes de independencia y
veredicto. Si la ronda provoca cambios, el resultado corregido se revisa otra
vez. Las pruebas mecánicas y una autorrevisión no cuentan como revisión
independiente.
