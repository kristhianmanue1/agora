# Selección offline de citas CTIM, páginas físicas 18 y 21

**Estado:** ensayo local de exportación; candidato para recotejo del consumidor,
sin admisión ni aceptación institucional. No se hicieron llamadas nuevas a
modelos ni se reprocesó el PDF.

Se usaron los candidatos GLM existentes de Ágora, los derivados y los
`exchange.json` de Skopos ligados al PDF local
`2900-003-001_RS1.pdf` (SHA-256
`1f8ad5e506b21cbf6b568b68790d2a757ba870524a6ba341f2dff3637d2494f2`).
Los manifiestos seleccionan rangos por afirmación sin alterar los candidatos ni
los paquetes v2 previos. `page18-refinement.json` y `page18-package/` son el
primer intento, conservado como control negativo: el cotejo del consumidor
encontró dos citas insuficientes. Su sustitución local es
`page18-refinement-v2.json` y `page18-package-v2/`.

| Página | Afirmaciones | Longitud original de cada cita | Bytes seleccionados por afirmación |
| --- | ---: | ---: | --- |
| 18, selección v2 | 4 | 1477 | 449, 307, 534, 509 |
| 21 | 3 | 582 | 135, 288, 169 |

Los paquetes `page18-package-v2/package.json` y `page21-package/package.json`
usan `agora/consultation-package/v3-experimental`. La reconstrucción offline
con `export-answer --citation-refinement ... --verify-package ...` verificó
ambos paquetes. El control negativo sintético cambia la selección de una
actividad 14 a la 15 con hash literal correcto y se rechaza con
`refinement_activity_mismatch`. Las pruebas también rechazan manifiesto
obsoleto, literal modificado, afirmación faltante y cita fuera de la original.

La corrección v2 mantiene las cuatro afirmaciones originales. A16 usa bytes
800–1334, que incluyen el supuesto de cédula no procedente, el `CPIM` de la
fila 16–17, la actividad 16 y la parte de la 17 que establece estatus y cierre.
A17 usa el `CPIM` de esa fila en 822–827, segmento `skopos-p18-item-29`, y
973–1477 para condición, actividad 17 y nota. La página física 18 se
inspeccionó visualmente en el PDF local.

`audit_page18_v2.py` comprueba que la selección cubra los fragmentos concretos
que sostienen esas dos afirmaciones y que A17 use el segmento del responsable
de la fila 16–17. Dos controles que sustituyen por separado A16 y A17 con sus
rangos anteriores fueron rechazados (`claim_2_required_source_span_missing`
y `claim_3_required_source_span_missing`). El primer paquete queda en disco
como antecedente, no como la versión recomendada para recotejo.

**Límite:** el reconocimiento del número de actividad es un guard estructural
estrecho; no comprueba actor, acción, objeto, destinatario ni suficiencia del
fragmento. Las etiquetas GLM/Jev previas se conservaron como históricas y el
respaldo de cada nueva cita quedó `not_reassessed_for_refined_citation`.
Corresponde al consumidor volver a cotejar visualmente el PDF y adjudicar cada
vínculo. El auditor local detecta estos errores conocidos, no todos los errores
semánticos posibles.
Los paths de Skopos y del PDF son locales; estos paquetes no son por sí solos
reproducibles en otra máquina sin esos insumos exactos.
