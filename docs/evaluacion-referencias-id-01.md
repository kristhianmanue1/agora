# Evaluación pareada de referencias por ID

2026-09-23. Implementación y evaluación acotada completadas. No se cambió el
modo predeterminado ni se promovió fiabilidad general.
Contrato: [referencias por ID](referencias-evidencia-por-id.md).

## Alcance

Cuatro pares, ocho llamadas a GLM 5.3 Flash, una versión de código congelada,
sin reintentos ni reparación. Misma fuente, pregunta y aspectos por par; orden
alternado. Temperatura 0; salida máxima 8192 tokens; timeout socket/proceso
180/200 segundos. Política: 12 referencias por aspecto, 12000 bytes de citas
por aspecto y 48000 totales; entrada hasta 40000 bytes, prompt hasta 200000.

G1 es el control conocido con seis párrafos seleccionados por el productor.
R1–R3 son documentos reales QASPER v0.3, ausentes de los dos pilotos previos y
de los ejemplos conocidos, seleccionados por ID ordenado, tamaño de 16–32 KB
y pregunta elegible respondible. Los modelos recibieron el documento completo,
no las anotaciones de referencia. Preguntas originales en inglés; salida
solicitada en español para ambos modos. No es puntuación oficial de QASPER.

Fuentes: QASPER, Dasigi et al., NAACL 2021, dataset CC-BY 4.0. Se verificó el hash
del dataset local; se conservaron sus marcadores de fórmulas/tablas. No se
consultaron PDFs editoriales ni se verificó contaminación de entrenamiento.

## Resultados observados

| Caso | Literal | IDs | Tokens literal / IDs |
|---|---|---|---:|
| G1, NaturalOWL conocido | Cita no literal; rechazo | Candidato aceptado | 8780 / 6357 |
| R1, objetivos de representaciones | Cita no literal; rechazo | Candidato aceptado | 7209 / 8564 |
| R2, datasets del Attention Sum Reader | Candidato aceptado | Candidato aceptado | 6529 / 9807 |
| R3, dataset de relaciones discursivas | Candidato aceptado | Candidato aceptado | 10598 / 12651 |

Literal: 2/4 aceptadas, 33116 tokens, 166.379 segundos acumulados.
IDs: 4/4 aceptadas, 37379 tokens, 125.849 segundos acumulados.
Total: **70495 tokens y 292.228 segundos**, sin timeout ni consumo desconocido.
Son tiempos de procesos, no preparación/revisión. Caché no controlada; no se
extrae una conclusión general de velocidad ni se calcula precio monetario.

Los IDs consumieron 12.9% más tokens en el conjunto, que incluye dos rechazos en
literal. No es una comparación a igual calidad. Incluso restringiendo a R2/R3,
ambos aceptados en los dos modos, IDs usó 22458 frente a 17127 tokens, 31.1% más.
El coste de metadatos y las diferencias de generación importan; usar IDs no
supone ahorro automático.

## Tamaño real de la evidencia

El presupuesto se aplica a unidades reconstruidas completas, no al ID corto.
Los candidatos por ID contienen 39 referencias con 36182 bytes de texto citado,
contando repeticiones; las dos respuestas literales aceptadas contienen 18 citas
con 1942 bytes. No comparar esos totales como si ambos tuvieran cuatro éxitos.
En los pares aceptados R2/R3, la comparación es 5175 bytes por ID frente a 1942
bytes literales. Referenciar párrafos completos puede ampliar mucho el paquete.

Se regeneraron las unidades y sus IDs desde cada envelope, se contrastó cada
span y anclaje con los bytes originales y se comprobaron todos los hashes de
código/entradas/resultados. Las 39 referencias por ID apuntan a unidades
suministradas y se resuelven literalmente; las 18 citas literales aceptadas
coinciden también con sus fuentes. No se aceptó ni reparó una cita alterada.

## Revisión del contenido

- **G1:** cubre los aspectos principales antes definidos: métodos, selección,
  resultados y límites automáticos, recursos manuales e idiomas. Una frase
  explica semillas como valores del identificador de relación; el pasaje lleva
  el marcador INLINEFORM2, por lo que su precisión matemática no se certifica
  desde esta representación. El ejemplo X/Y es paráfrasis en la afirmación;
  el texto de evidencia reconstruido mantiene sus marcadores originales.
- **R1**, artículo `1602.03483`: identifica SDAEs y FastSent, conforme a las dos
  anotaciones originales. Añade detalles sobre entrenamiento y variantes. La
  respuesta por IDs salió **en inglés pese a solicitar español**; se registra
  como incumplimiento de idioma, no como fallo de referencia. El validador no
  comprueba idioma. La literal fue rechazada por alterar un extracto del método.
- **R2**, `1603.01547`: ambas identifican CNN, Daily Mail y CBT, incluidos CN/NE
  en los detalles. La variante por IDs expresa primero uso/evaluación y después
  menciona entrenamiento. Los nombres requeridos están presentes. Los detalles
  adicionales no eran necesarios para responder y aumentan extensión/evidencia.
- **R3**, `1603.03876`: ambas identifican PDTB 2.0 y conservan las particiones
  2–20, 21–22 y 0–1. Literal aporta más detalles no pedidos. Los datos principales
  coinciden con las anotaciones originales y los pasajes.

Esta es autorrevisión del productor, no adjudicación independiente. Las
anotaciones públicas pueden contener errores. Presencia de hechos esperados no
certifica cada inferencia adicional. Un ID válido no demuestra entailment:
una prueba local acepta una atribución falsa con ID real y mantiene
`semantic_support: not_verified` y `coverage: not_verified`.

## Implementación y pruebas

Nuevo módulo `evidence_ids.py`, opción `--citation-mode ids` en evidence_cli,
contrato `agora/claim-evidence-query/v2`. Modo literal v1 intacto por defecto.
La respuesta original del proveedor se conserva; las citas se resuelven según
el contrato. IDs desconocidos, de otra revisión, duplicados y textos de cita
suministrados por el modelo se rechazan. JSON inválido sigue rechazándose.

**216 pruebas pasan**. Nuevas regresiones: identidad de fuente/revisión,
literalidad con UTF-8, offsets, segmentación larga, presupuesto sobre citas
resueltas, duplicados, ubicación exacta con textos idénticos, aspectos ausentes,
abstención y semántica no verificada. `git diff --check` sin errores.
Código no modificado durante las llamadas; auditoría reproducible en
`experiments/evidence-ids-v1/audit.py`. Resultados locales en `runs/glm-01`,
excluidos de Git. No hubo commit, push ni escritura de memoria.

## Decisión

Mantener IDs como opción experimental: elimina la necesidad de copiar citas y
funcionó en estos cuatro casos, pero añade tamaño y no garantiza idioma,
respaldo semántico, cobertura ni formato válido en toda ejecución.

Próximo trabajo útil: control explícito de idioma, unidad de evidencia más
ajustada sin perder contexto y revisión de afirmaciones adicionales no pedidas.
Después evaluar otra muestra real con criterios y revisión separados. No
promover automáticamente el modo ni afirmar ahorro por estos resultados.
