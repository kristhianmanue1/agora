# Lectura selectiva frente a completa: ahorro con una excepción omitida

**No se demuestra todavía “leer menos sin perder lo importante”.** La selección
reduce texto y tokens, y ambas respuestas pasan la rúbrica y el contraste de
respaldo. Sin embargo, la completa incluye una excepción de pertenencia al conjunto
de datos ausente del contexto selectivo: Automotive se excluye en el escenario
10-core. Este caso expone un límite de la recuperación y de la rúbrica estrecha.

## Diseño

QASPER `2001.04346`, seleccionado por hash y exclusión del inventario local previo;
34.053 bytes. Pregunta: “Which set of datasets do they use?”. La rúbrica congelada,
extraída de la primera anotación humana, exige nueve datasets de Amazon y Yelp.
No incluye la excepción detectada después. Se conserva sin cambiar sus etiquetas.

Dos brazos, candidatos originales sin reparación, misma instrucción de agrupación,
modelo, 4.096 tokens máximos de generación y límites de citas:

- Selectivo: recuperación léxica existente, sólo la pregunta, sin rangos de
  referencia; presupuesto 8.000 bytes, top-k 4, entrega efectiva 5.145 bytes.
- Completo: los 34.053 bytes de fuente.

El recuperador local escanea el archivo completo. La reducción es de texto enviado
al modelo, no de lectura de disco. La selección no consultó las anotaciones ni la
rúbrica. Los prompts efectivos y fuentes se conservan por hashes.

GLM evaluó cobertura por rúbrica. Jev evaluó cada afirmación sólo contra sus propias
citas, sin las etiquetas de cobertura. Para declaraciones de ausencia, sólo vio los
pasajes leídos por ese brazo; el nombre heredado `full_source_for_missing_only` del
payload no implica acceso a contenido fuera del contexto selectivo, y las
instrucciones precisan esa limitación.

## Resultados

| Medida | Selectivo | Completo |
|---|---:|---:|
| Bytes de fuente enviados al generador | 5.145 | 34.053 |
| Tokens de entrada del generador | 1.875 | 11.379 |
| Tokens: generación + dos revisiones | 5.164 | 26.504 |
| Segundos acumulados de llamadas | 13,704 | 45,112 |
| Bytes de citas | 2.082 | 4.611 |
| Requisitos cubiertos | 2/2 | 2/2 |
| Afirmaciones según Jev | 2 supported | 4 supported |
| Ausencia declarada según Jev | No hubo | supported |

Reducción observada: 84,89% en bytes de fuente para el modelo, 83,52% en tokens de
entrada del generador y 80,52% en tokens sumados de las tres llamadas por brazo.
No es una estimación general ni comparación a calidad equivalente. El brazo completo
produjo más detalles y una ausencia que añadió trabajo al revisor. No se contabilizan
trabajo humano, preparación de rúbrica, lectura local o todo el ciclo del sistema;
no se dispone de coste monetario. Seis llamadas, 31.668 tokens en total.

## Hallazgo fuera de la rúbrica

La fuente dice que Automotive se excluye de resultados 10-core porque quedan pocos
usuarios e ítems. La respuesta completa lo conserva. Ni el contexto seleccionado
ni su respuesta contienen ese matiz. El pasaje y sus offsets se guardan en
`result.json`; `verify.py` verifica su literalidad y su ausencia del contexto elegido.

Clasificación del productor: información presente en la fuente pero perdida en la
selección, potencialmente material porque cambia qué datasets integran un escenario.
No es una alucinación demostrada ni un juicio independiente sobre toda la respuesta.
La rúbrica de dos requisitos y el control de respaldo de afirmaciones no detectaron
ese faltante: cubrir una lista y citar correctamente lo afirmado no mide todo lo
omitido. No se alteran retrospectivamente los resultados favorables de esos controles.

## Verificación e incidente local

`verify.py` reconstruye fuentes, candidatos sin cambios, localizadores, rúbricas,
prompts y recuperación usando sólo la pregunta. También comprueba la separación de
entradas del revisor. Cero HTTP. Antes de las llamadas, un archivo `select.py` entró
en conflicto con el módulo estándar; se renombró `prepare_selection.py`. No hubo
solicitudes al proveedor durante ese fallo ni cambios de caso por resultados.
Originales completos en carpetas locales ignoradas; respuestas y hashes en resultado.
Sin cambios de producto ni repetición de suite general. Sin promoción de defaults.

## Siguiente paso

Construir un control explícito de condiciones/excepciones: ampliar la recuperación
cuando la respuesta general depende de configuraciones que puedan cambiar la lista.
Usar este caso ya conocido como regresión, sin fingir que sigue reservado; contrastar
la estrategia en otra fuente nueva. Conservar qué leyó cada etapa y sumar sus costes.
Si no alcanza evidencia suficiente, declarar el alcance parcial o ampliar la lectura.
No incorporar la excepción a escondidas usando la respuesta completa como oráculo
ni aceptar sólo porque ambos revisores emitieron etiquetas favorables.
