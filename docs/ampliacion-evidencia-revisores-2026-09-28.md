# Ampliar con evidencia pertinente cambia el resultado

## Resultado del ensayo

24 llamadas nuevas, 12 por proveedor; todas válidas y sin reintentos. Se conservaron
los dos juicios originales por proveedor. No se modificó su evidencia ni se
sustituyó un revisor predeterminado. GLM conserva su función de generador.

| Evidencia entregada | Bytes de evidencia | GLM correcto | Jev correcto |
|---|---:|---:|---:|
| Abstract solo | 1686 | 2/4 | 0/4 |
| Abstract + párrafo general | 3071 | 2/4 | 0/4 |
| Abstract + párrafo decisivo | 3063 | 4/4 | 4/4 |

Cada condición tiene dos afirmaciones opuestas con dos repeticiones: no son cuatro
problemas independientes. Los criterios fueron fijados antes de llamar. El párrafo
general y el decisivo tienen tamaños parecidos: 1383 y 1375 bytes. Esto aporta un
control frente a la explicación «mejoró por recibir más texto», limitado a este caso.

El párrafo decisivo especifica que los modelos ILP dependen de un planificador de
texto externo. Ambos revisores entonces respaldaron la dependencia externa y
contradijeron la afirmación de que realizan esa planificación internamente.
Las cuatro respuestas de cada modelo con ampliación pertinente coinciden con sus
criterios y se mantienen en ambas repeticiones. Sin ese pasaje, Jev repitió los
mismos errores; GLM varió entre repeticiones del abstract solo pese a temperatura 0.
Estabilidad de salida y corrección son propiedades distintas.

## Qué significa para Ágora

Podemos proporcionar evidencia puntual suficiente para estas dos afirmaciones sin
enviar el documento completo de 116094 bytes. Los 3063 bytes equivalen al 2.64%
del texto completo. Es una comparación de bytes de evidencia suministrada, no un
ahorro monetario del sistema ni una garantía de cobertura de todos los temas.
La selección y verificación locales sí consultaron el documento completo.

Las nuevas llamadas fueron independientes: no se enviaron el juicio anterior ni
las etiquetas esperadas. Por tanto, se observó una nueva evaluación correcta con
evidencia ampliada, no una explicación del modelo sobre cómo corrigió su error.
Los originales permanecen consultables y vinculados por hashes en originals.json
 y lineage.json. Los derivados conservan admission=not_admitted.

## Límites y autorrevisión

- Es desarrollo sobre un fallo conocido; no holdout ni revisión independiente.
- El productor localizó el pasaje por una frase conocida del texto. No existe aquí
  un recuperador que descubra automáticamente la evidencia necesaria.
- Dos repeticiones detectan algunas variaciones, pero no estiman fiabilidad general.
- El experimento no demuestra cómo reconocer cuándo falta evidencia. Un supported
  o el acuerdo entre modelos tampoco acredita que el fragmento sea suficiente.
- El helper expansion.py comprueba revisión y localizador UTF-8, no pertinencia
  semántica ni autoridad. La recuperación automática sigue sin estar implementada
  por este incremento. No se añadió vigilancia ni admisión en AN-KLA.

## Próximo incremento recomendado

Construir un flujo explícito, inicialmente manual: seleccionar una afirmación,
solicitar ampliación, recuperar candidatos de pasajes con el adaptador existente,
mostrar procedencia y ejecutar una nueva revisión conservando la anterior. Primero
medir si el recuperador encuentra el pasaje sin conocer su frase exacta ni el gold;
no atribuir a Jev ni GLM un fallo que en realidad sea evidencia no recuperada.

Mantener límite de bytes y número de expansiones; si la evidencia no alcanza,
conservar la cuestión pendiente. No activar ese flujo por una confianza numérica
escogida después del fallo. Validarlo después con nuevos casos reservados.

## Consumo y verificación

GLM: 8486 tokens de entrada y 4146 de salida, 12632 total; suma de duraciones
125.030 s. Jev: 11162 de entrada y 546 de salida, 11708 total; 3.231 s.
No se verificó cargo monetario. No se midió ahorro del trabajo completo de selección.

430 tests pasan, incluidos tres nuevos para revisión de fuente, rangos, Unicode
y conservación del contenido anterior. Se verificaron inputs congelados, payloads
idénticos por proveedor, respuesta contra parser y todos los hashes parentales sin
cambios. La puntuación se implementó durante la tanda con criterios ya congelados.

[Protocolo](../experiments/evidence-expansion-v1/README.md),
[resultados](../experiments/evidence-expansion-v1/result-01.json),
[linaje](../experiments/evidence-expansion-v1/lineage.json),
[originales](../experiments/evidence-expansion-v1/originals.json).
Fuente: QASPER v0.3, Dasigi et al., documento 1811.00051, corpus CC-BY 4.0;
representación textual del corpus, no PDF editorial. Entradas completas locales
ignoradas; recibos publicados sin repetir el documento.
