# Suficiencia con fuente mayor: una omisión invisible al juez

## Resultado

El ensayo detectó una falsa suficiencia: la búsqueda recuperó tres fases de un
programa de cuatro; el juez consideró la evidencia completa y la respuesta afirmó
que el programa tenía tres fases. Las citas eran literales. Por tanto, ni la
literalidad ni un segundo juicio del modelo garantizan cobertura global.

Se mantiene exclusivamente observación. No se activó búsqueda adicional ni
admisión de memoria. Evaluación y respuesta fueron llamadas prefijadas separadas:
la respuesta no recibió ni obedeció el juicio de suficiencia.

## Cambio y método

Se hizo explícito que `decision` usa únicamente los valores ingleses `sufficient`,
`insufficient`, `uncertain`; explicaciones y faltantes siguen en español. El validador
continúa rechazando traducciones, mayúsculas y espacios añadidos, sin reparación.
Suite local: **119 pruebas OK**, incluida la nueva regresión de enums. Esto endurece
la instrucción y conserva la validación, no impone generación restringida al proveedor.

Ensayo `experiments/sufficiency-large-v1/runs/glm-01`, 22 de septiembre de 2026:
fuente sintética de **144 748 bytes**, datos separados por relleno repetitivo,
tres preguntas nuevas, doce solicitudes como máximo y efectivamente realizadas.
Comparación entre recuperación léxica (top 3 más vecinos, 2 048 bytes) y pasajes de
referencia completos seleccionados por el productor. Cada ruta tiene juez y respuesta.
Referencia es un control positivo, no un recuperador automático ni lectura completa.

Preguntas, criterios, fuente, código y protocolo quedaron congelados antes de
llamar. Se verificaron **15 archivos congelados y 12 resultados** por SHA-256;
envoltorios de juez y respuesta iguales en cada pareja. Modelo solicitado y
reportado: `glm-5.3-flash`, sin comprobación independiente del proveedor; temperatura
0, 2 048 tokens máximos de salida, socket 90 s y deadline 110 s por operación,
sin reintentos. Credencial del laboratorio sólo en entorno, nunca registrada.

## Resultados contrastados con la fuente

| Pregunta | Recuperación y juez | Respuesta recuperada | Control de referencia |
|---|---|---|---|
| L1: responsable e importe, secciones alejadas | Ambos datos; sufficient | Nerea y 118 créditos, correcto | Correcto |
| L2: persona al frente, distractores temáticos | Falta Eloy; insufficient | Abstención adecuada; tarea sin resolver | Eloy, correcto |
| L3: todas las fases y responsables | Falta fase final; sufficient **erróneo** | Afirma tres fases y omite a Darío | Cuatro fases, correcto |

Se observaron **seis juicios con formato válido**, con una falsa suficiencia entre
los dos contextos deliberadamente incompletos. El formato correcto no corrigió el
fallo semántico. En L3 el juez y el generador hicieron la misma generalización:
confundieron lo seleccionado con la totalidad del original.

La autorrevisión adversarial verificó citas, explicaciones, respuestas y omisiones
contra la fuente congelada. No participó un revisor independiente en este incremento.
Los nombres detectados automáticamente en métricas se contrastaron con el significado
de las frases; contar coincidencias por sí solo no sería evaluación semántica.

## Coste observado

| Ruta, tres preguntas | Tokens juez | Tokens respuesta | Total | Segundos de procesos | Bytes locales leídos |
|---|---:|---:|---:|---:|---:|
| Recuperación | 3 555 | 3 000 | 6 555 | 82,282 | 4 776 684 |
| Referencia | 2 273 | 2 376 | 4 649 | 54,610 | 3 908 196 |

Total: **11 204 tokens**, **136,892 segundos**. Son tokens reportados por proveedor;
no se calculó importe monetario. Los bytes locales cuentan lecturas lógicas de la
fuente por este ensayo, incluidas verificaciones y preparaciones repetidas; no miden
I/O físico de disco. Se enviaron pasajes pequeños, pero el archivo se releyó completo
localmente. El juez agregó 5 828 tokens a los 5 376 de generación de respuestas.
No hay baseline con modelo leyendo toda la fuente, por lo que no se demuestra ahorro.

## Qué sigue

1. Separar **suficiencia del contenido recibido** de **cobertura de la fuente**.
   Para preguntas globales, el consumidor debería exigir evidencia de recorrido o
   cobertura y devolver cobertura desconocida si falta. La etiqueta del juez por
   sí sola no debe permitir afirmar exhaustividad.
2. Probar un recorrido acotado por secciones para preguntas globales y una segunda
   estrategia de recuperación para fallos como L2. Declarar presupuesto y faltantes;
   no pasar automáticamente a enviar todo el documento.
3. Evaluar luego documentos reales autorizados y preguntas preparadas sin ajustar
   el prompt a ellas. Medir omisiones, citas, cobertura y coste conjunto.

No se estima precisión general con este único documento artificial. Tampoco se
atribuye causalmente el cumplimiento del enum al nuevo prompt: cambió el corpus y
no hubo comparación controlada. El fallo E5 anterior se conserva sin reinterpretar.
Ágora sigue independiente de Skopos y AN-KLA; estos mecanismos deben funcionar con
fuentes locales y admitir futuros adaptadores mediante contratos opcionales.

Cambios locales, sin commit ni push; AGENTS.md y memorias sin modificación.

## Incremento posterior

El [control de cobertura global](cobertura-global.md) bloquea el caso L3 en una
nueva API explícita, sin reinterpretar este resultado ni certificar semántica.
Todavía no ejecuta el recorrido por partes ni protege automáticamente las CLI anteriores.
