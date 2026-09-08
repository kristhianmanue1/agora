# Base experimental Ágora–SKEVI v1

Esta carpeta materializa el controlador neutral de
`agora-skevi-experiment/v1`. Verifica el freeze y puede preparar el manifest de
una corrida futura. No implementa la vertical slice, no instala SKEVI y no
ejecuta productores, reviewers ni fixtures.

## Componentes

- `experiment.lock.json`: proyección ejecutable del contrato documental
  congelado. Los Markdown y la revisión Git indicada conservan la autoridad que
  les asigna la matriz del proyecto.
- `schemas/run-manifest.schema.json`: forma cerrada de una corrida preparada.
- `scripts/verify_freeze.py`: recalcula digests de archivos y secciones.
- `scripts/prepare_run.py`: crea un run manifest fuera del repositorio después
  de verificar el freeze. No inicia la corrida.
- `tests/`: verifica integridad, asignación C0/C1 y fail-closed.

## Verificación

```bash
python3 experiments/agora-skevi-v1/scripts/verify_freeze.py
python3 -m unittest discover -s experiments/agora-skevi-v1/tests -v
```

Preparar un manifest requiere un `agora_base_commit` ya construido y un destino
externo nuevo:

```bash
python3 experiments/agora-skevi-v1/scripts/prepare_run.py \
  --run-id <id> --pair-id <1..3> --condition <C0|C1> \
  --base-commit <sha-completo> --output /ruta-aislada/run.json
```

El comando sólo prepara datos. La ejecución del piloto requiere autorización y
un runner separado que esta base no incluye.
