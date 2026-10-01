# Recuperación explícita ante cobertura incompleta

`coverage-plan` produce una propuesta `agora/coverage-recovery-proposal/v1-experimental`
desde un candidato y una revisión `review-rubric` conservados. Verifica hashes,
pregunta, parte, etiquetas contra respuesta guardada y pasajes contra fuente.
Conserva el contexto anterior y agrega párrafos dentro de un presupuesto total.
No llama a proveedores, no genera otra respuesta ni admite memoria.

Ejemplo, desde la raíz, con workspace previamente inicializado:

```bash
PYTHONPATH=src python3 -m agora.issue_cli --workspace /ruta/workspace coverage-plan \
  --source /ruta/source.txt --source-sha256 HASH_FUENTE \
  --candidate /ruta/candidate.json --candidate-sha256 HASH_CANDIDATO \
  --rubric /ruta/rubric.json --rubric-sha256 HASH_RUBRICA \
  --review /ruta/result.json --review-sha256 HASH_REVISION \
  --part-id P1 --question 'What metrics are used to measure bias reduction?' \
  --query metrics --query-origin 'Término de la pregunta original' \
  --budget 12000 --top-k 3 --following 3 --out /ruta/proposal.json
```

`--query` acepta de una a cuatro consultas explícitas; su origen es declarado por
el llamador, no verificado. El código no añade textos de la rúbrica a las consultas;
esto no impide que un llamador suministre términos procedentes de ella. Los IDs de
requisitos faltantes disparan la propuesta; no sirven como respuestas de búsqueda.
El recuperador léxico existente lee la fuente completa localmente. El presupuesto
mide bytes UTF-8 del contexto combinado, no tokens, coste de API ni lectura de disco.
`--following` agrega hasta tres párrafos posteriores a cada tramo recuperado;
su valor predeterminado es cero. Puede añadir información irrelevante.

## Paradas y límites

- `requires_review`: hay requisitos inciertos o contradictorios; no busca.
- `no_expansion`: no hay faltantes en la rúbrica suministrada; no demuestra que
  la rúbrica sea completa ni que la respuesta sea globalmente suficiente.
- `no_new_passages`: no se pudo añadir contexto dentro del presupuesto; no prueba
  ausencia de la respuesta en la fuente.
- `proposed`: queda una propuesta para ejecución explícita. Preserva los originales,
  fija sus hashes y rechaza sobrescribir el archivo de salida.

Una revisión conservada puede estar equivocada. Los hashes acreditan vinculación,
no verdad, autenticidad del revisor ni adjudicación independiente. Fuentes hasta
160.000 bytes en esta CLI; no es todavía la solución para fuentes arbitrariamente grandes.

La propuesta **no es entrada compatible con `generate-plan`**: éste verifica otro
contrato. El consumidor `generate-recovery` descrito abajo verifica identidad, límites y
procedencia antes de producir un candidato derivado. No cambiar el schema para
eludir esa comprobación.

## Evidencia

[Regresión local](../experiments/coverage-recovery-v1/README.md): las definiciones
omitidas de ΔG y ΔS se recuperan. No se ejecutó generación posterior ni una prueba
ciega; no hay promoción de parámetros predeterminados.

## Generar un candidato derivado

`generate-recovery` consume explícitamente esta propuesta. Requiere los mismos
argumentos `--source`, `--candidate`, `--rubric`, `--review`, sus cuatro hashes,
`--part-id` y `--question`, además de:

```text
--proposal /ruta/proposal.json --proposal-sha256 HASH_PROPUESTA
--response-language en --live --out /ruta/directorio-nuevo
```

Para reproducción sin red, sustituir `--live` por `--response /ruta/response.json`.
La implementación reconstruye la propuesta con el recuperador vigente y exige
igualdad exacta, incluido su hash de implementación. Rechaza versiones incompatibles,
propuestas modificadas y estados distintos de `proposed` antes de llamar al modelo.

La salida conserva request, respuesta del proveedor y candidato con los hashes del
padre, revisión y propuesta. Reserva un directorio nuevo; nunca reutiliza uno existente.
Registra `attempted` antes de llamar: una interrupción puede dejar ese estado, que no
prueba éxito ni fracaso remoto. No hay reintento automático. El límite es una llamada
GLM, 4.096 tokens de salida y 90 segundos; la entrada usa sólo los rangos reconstruidos,
citas por ID y un límite de prompt de 100.000 bytes. Los requisitos de la rúbrica no se
envían al generador. La validez estructural no demuestra fidelidad ni cobertura.

La revisión posterior sigue siendo explícita: `review-rubric` usa el candidato nuevo
y su hash; la fidelidad se contrasta por separado. `generate-plan` conserva su contrato.

Para decidir explícitamente si ampliar: [recorrido con revisiones vinculadas](lectura-revisada-cli.md).
