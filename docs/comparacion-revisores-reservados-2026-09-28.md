# Revisores GLM y Jev: evidencia externa y documentos grandes

2026-09-28. Tanda completada: 72 llamadas, 36 por proveedor; sin errores de
transporte, salidas inválidas, reintentos ni truncamiento de fuentes. No se cambió
el generador GLM ni se promovió un revisor predeterminado.

## Resultado

| Batería | GLM: coincide con gold | Jev: coincide con gold | Aceptación sin respaldo según gold: GLM / Jev |
|---|---:|---:|---:|
| AttrScore reservado | 20/24 | 21/24 | 0 / 0 |
| Documento completo | 6/6 | 6/6 | 0 / 0 |
| Sólo abstract | 4/6 | 4/6 | 1 / 1 |

Los 24 casos AttrScore conservan etiquetas externas. Los controles de documentos
largos tienen criterios del productor; no mezclar sus aciertos con AttrScore ni
presentarlos como adjudicación independiente. Cada control full/abstract comparte
la misma afirmación: las doce variantes no son observaciones independientes.

En AttrScore, ambos coinciden con gold en 20 casos. Jev coincide en uno adicional;
los otros tres producen desacuerdos de ambos. Macro-F1 de AttrScore: GLM 0.8370, Jev 0.8773. En los controles largos faltan
clases en algunos grupos; su macro-F1 de tres clases incluye ceros y no debe
compararse directamente con AttrScore. La ventaja de un caso es pequeña y
no acredita superioridad general. Ninguno marcó supported una respuesta cuyo gold
era contradicted o insufficient en esta selección.

## Hallazgo material: alcance de la evidencia

En *Generating Texts with Integer Linear Programming*, el abstract describe
selección de contenido, lexicalización y agregación. No establece si los modelos
realizan text planning internamente. El cuerpo sí declara que dependen de un
planificador externo. Se fijaron afirmaciones opuestas sobre esa propiedad y se
entregaron por separado el abstract y el documento completo.

El abstract exige insufficient en ambas afirmaciones. Ambos revisores cometieron
los mismos dos errores. Jev y GLM clasificaron como supported
que los modelos realizan text planning internamente y como contradicted que
recurren a un planificador externo. Los resultados de ambos con el documento completo sí
coincidieron con los criterios. Para la aceptación incorrecta en abstract reportó
confidence 0.4: no se había fijado un umbral de abstención y no se inventó uno
posterior para excluir ese error de las métricas.

La coincidencia de GLM y Jev en esos errores muestra que un acuerdo entre modelos
no sustituye evidencia suficiente.

Esta evidencia impide tratar una revisión positiva de un fragmento como garantía
sobre todo el documento. El problema puede estar en la información entregada y
en la inferencia del revisor, aunque formato y cita sean válidos.

## Lectura crítica de AttrScore

Se mantienen los tres desacuerdos compartidos sin reetiquetar después:
- Una referencia asigna una persona a tutoriales, mientras la respuesta la asigna
  a demostraciones: ambos predicen contradicted; gold dice Extrapolatory.
- Una respuesta coincide en cifra y fecha, pero atribuye la fuente a un portal
  que no aparece en el fragmento: gold dice Attributable; GLM insufficient y Jev
  contradicted. No hay adjudicación independiente de esta atribución.
- Una referencia menciona una conjunción astronómica de julio y la respuesta añade
  fechas de enero: ambos predicen insufficient; gold dice Contradictory.

Concordancia con el benchmark y juicio de verdad son propiedades diferentes.
Las etiquetas externas mejoran la comparación, pero no eliminan toda ambigüedad.

## Coste y latencia

GLM reportó 148,689 tokens totales; Jev reportó 152,951 sumando entrada y salida. Las duraciones de peticiones sumaron 325.556 s y 11.509 s, respectivamente.


Jev: 151301 tokens de entrada; a USD 0.042 por millón, la estimación es
USD 0.006354642 (salida gratuita según tarifa consultada). No es un cargo
verificado del ledger. No se obtuvo coste monetario comparable de GLM.
La [documentación de modelos de TypeSafe](https://docs.typesafe.ai/models)
se consultó el 2026-09-28. La toma única no controla red, caché ni variabilidad.
Los modelos reportados fueron glm-5.3-flash y jev-1.13.0.

## Decisión recomendada

**Mantener Jev como candidato opcional; no sustituir todavía al revisor por defecto.**
El siguiente incremento debe probar ampliación explícita de evidencia cuando una
conclusión relevante depende de información fuera del fragmento. Conservar el
resultado original y registrar el nuevo juicio al incorporar el pasaje necesario.
No basta con aplicar un umbral de confidence escogido después de ver el error.

Antes de promoción: adjudicar los desacuerdos, fijar una política de abstención o
ampliación en desarrollo y medirla en un conjunto distinto; repetir los casos
sensibles para medir estabilidad. La cobertura de resúmenes globales sigue pendiente:
este ensayo revisa afirmaciones y no cuenta información importante omitida.

## Procedencia y verificación

- [Protocolo congelado](../experiments/reviewer-comparison-v2/README.md),
  [selección](../experiments/reviewer-comparison-v2/selection.json),
  [resultados y matrices](../experiments/reviewer-comparison-v2/result-01.json).
- AttrScore: revisión 467dcdd2cd31f9b5e8625491f3bdf7af90943a8d; se excluyeron
  los 36 casos previos por pregunta, respuesta o referencia normalizada.
- QASPER: documentos 1811.00051 (116094 bytes) y 1911.03977 (68344 bytes),
  no utilizados en los pilotos locales anteriores; corpus CC-BY 4.0, Dasigi et al.
  Se usa su representación textual, no el PDF editorial ni tablas ausentes.
- Hashes de protocolo, entradas y ejecutor congelados antes de las llamadas.
  Puntuador implementado después de iniciarlas, con métricas previstas en protocolo;
  verificó cada petición contra el caso y cada etiqueta contra la salida guardada.
- Registros publicados sin copiar documentos completos: records-glm.jsonl y
  records-jev.jsonl. Entradas y peticiones completas permanecen locales en inputs/
  y directorios temporales; se reproducen con el corpus y el preparador identificados.
- 427 tests pasan. Autorrevisión, no revisión independiente. La auditoría adicional
  del CSV confirmó selección y textos idénticos con un lector que conserva saltos
  internos. El preparador congelado usa splitlines: no afectó estos casos, pero
  debe corregirse antes de reutilizarlo en otra selección.
