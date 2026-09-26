# Contrato explícito de afirmaciones y evidencia

Implementación local experimental: `agora/claim-evidence-query/v1`.
No sustituye ni reinterpreta los contratos históricos de consulta.

## Bloque 1: límites y diagnósticos

`EvidencePolicy` configura máximo de citas por aspecto, bytes UTF-8 de citas por
aspecto y bytes totales, contando repeticiones. Valores iniciales: 12, 12000 y
48000; son límites operativos conservadores, no valores óptimos demostrados.
Techos configurables: 96 citas por aspecto, 1 MiB por presupuesto de bytes.
El prompt se construye con la política efectiva; el resultado conserva esa misma
política. La ruta antigua conserva su máximo 12 y reglas de aceptación: sólo
se añadió al prompt base el máximo que ya exigía el validador, usando la misma
constante. Su diagnóstico histórico no se reinterpreta.

El contrato nuevo recoge errores independientes: cantidad, bytes, duplicados
idénticos dentro de una afirmación, literalidad, forma y consistencia de estados.
No detiene la inspección de citas al encontrar exceso de cantidad; puede mostrar
simultáneamente ese defecto y una cita alterada. Un mismo pasaje puede respaldar
varias afirmaciones; repetirlo entre afirmaciones se permite y se cobra en cada
ocurrencia. No se elimina ni recorta evidencia para hacer pasar una respuesta.

## Bloque 2: afirmación, respaldo propuesto y pendiente

El llamador proporciona de uno a ocho aspectos `{id, question}`. El modelo
propone para cada uno:

- `status`: `answered`, `partial` o `not_in_passages`.
- `claims`: hasta 16 afirmaciones `{text, quotes}`; texto de hasta 6000 caracteres.
- `missing`: hasta 16 lagunas, cada una de hasta 2000 caracteres.

Cada afirmación lleva sus propias citas. Las citas deben existir enteras dentro
de un pasaje, y los anclajes identifican aspecto, afirmación y cita mediante
índices. No se permiten uniones artificiales entre pasajes separados.

`answered` exige afirmaciones y ninguna laguna; `partial` exige ambas;
`not_in_passages` exige sólo lagunas. Son **declaraciones del modelo**, no
veredictos. La salida mantiene `semantic_support: not_verified` y
`coverage: not_verified`. `review_queue` enumera afirmaciones pendientes de
contraste; `coverage_review` conserva estado/lagunas propuestos por aspecto y
su cobertura no verificada. `candidate_partial` indica una laguna declarada,
no detecta automáticamente las que el modelo olvidó declarar.

Una afirmación falsa que cita una frase literal puede superar esta validación.
Una prueba lo demuestra explícitamente. El contrato facilita revisar el vínculo;
no implementa inferencia textual, adjudicación independiente ni certificación.
No es admisión en memoria ni publicación.

## Uso

```bash
PYTHONPATH=src python3 -m agora.evidence_cli \
  --source fuente.txt --source-id documento --sha256 HASH \
  --question 'Pregunta global' --aspects aspectos.json \
  --content-budget 12000 --prompt-budget 200000 \
  --max-quotes-per-part 12 --max-quote-bytes-per-part 12000 \
  --max-quote-bytes-total 48000 --model glm-5.3-flash \
  --max-output-tokens 8192 --timeout-seconds 180 --out salida-nueva
```

`--range inicio:fin` repetible permite usar pasajes con anclajes del original.
Sin rangos se intenta la fuente completa dentro del presupuesto. La CLI no hace
recuperación automática, llamadas adicionales, reparaciones ni retries.
`ZAI_API_KEY` se obtiene del entorno y no se registra. No se solicita JSON mode
al proveedor; se conserva validación local estricta y límite de respuesta HTTP.

## Compatibilidad y límites

Los consumidores anteriores siguen disponibles. El contrato nuevo requiere
adopción explícita por un consumidor; no reemplaza sus campos ni normaliza
resultados viejos. Los fixtures/receipts anteriores permanecen inalterados.
El prompt base antiguo cambió; sus ejecuciones nuevas deben distinguirse de las
históricas por sus hashes congelados. No comparar las dos interfaces como si
sólo cambiara una variable: el contrato nuevo también estructura la respuesta
por aspectos y cambia su presupuesto total potencial.

No hay revisión semántica automática, selector por aspectos autónomo ni garantía
de escalabilidad. La validación nueva no declara correctas citas sólo por tener
anclajes; comprueba literalidad. La revisión final sigue siendo necesaria.

## Verificación y evaluación

Las pruebas de regresión cubren frontera 12/13 sin duplicados, presupuesto UTF-8,
configuración, errores simultáneos, omisión de aspectos, JSON duplicado,
consistencia de estados, pasajes separados y la limitación semántica explícita.
El bloque 3 está definido en `experiments/evidence-contract-v1`: una regresión
legacy del control conocido y cinco llamadas del contrato nuevo (G1 y cuatro
casos sintéticos nuevos). Entradas, criterios, código y protocolo se congelan
antes de llamadas, sin ajustes durante la campaña. Los casos nuevos son del
productor, no una revisión independiente ni benchmark público.

## Variante de referencia por ID

Disponible como opción explícita y contrato v2: [referencias por ID](referencias-evidencia-por-id.md).
La [evaluación pareada](evaluacion-referencias-id-01.md) conserva fallos, costes
y límites; v1 literal sigue siendo el modo predeterminado.
