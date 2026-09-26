# Respuesta breve y abstención por alcance

Incremento local, 2026-09-23. Perfil opt-in `concise-v1`; no sustituye la línea
base QASPER ni constituye revisión semántica automática.

## Cambio

API: `query_routed(..., answer_profile='concise-v1')`.
CLI: `--answer-profile concise-v1`, combinado con `--response-language es|en`.
El valor predeterminado `legacy` conserva el prompt y formato v0.2 anteriores.
El nuevo perfil emite `agora/routed-query/v0.3`; sus partes tienen exactamente:
`id`, `status`, `answer`, `explanation`, `quotes`.

- `answer`: dato solicitado, breve pero completo; hasta 1000 caracteres.
- `explanation`: justificación separada, 1–2000 caracteres no vacíos.
- `quotes`: hasta 12 fragmentos literales para respaldar respuesta y explicación.
- Abstención: `status=not_in_document`, `answer=""`, `quotes=[]`; explicación
  del vínculo que falta, sin presentar la conclusión solicitada como conocida.

Los límites rechazan, no truncan. Cifras, unidades, condiciones y conflictos
materiales deben permanecer en answer; explanation no debe esconder un matiz
que cambie la respuesta. El exportador QASPER puntúa answer únicamente; las
citas siguen generando evidencia por párrafo. No se modifica el evaluador oficial.

La instrucción nueva exige distinguir sujeto, estudio, población, tiempo y
propiedad solicitada. Descripción general no prueba método concreto; finalidad
del programa no prueba resultados; resultado de otro grupo no prueba el grupo
consultado. Una negación explícita o un conflicto documentado sí son respuestas
posibles: no se debe convertir prudencia en abstención universal.

## Qué comprueba el software

Comprueba formato, campos, límites, IDs, citas literales, anclas y presupuestos.
Mantiene `semantic_support=not_verified`. No comprueba automáticamente que una
cita implique la afirmación, ni que la explicación sea correcta. Incluso una
respuesta falsa con una cita verdadera puede pasar: una prueba conserva visible
este límite. Las explicaciones de abstención son afirmaciones del productor,
no auditorías independientes. En recuperación parcial, not_in_document significa
no establecido en los pasajes consultados; no demuestra ausencia en toda la fuente.

## Desarrollo y evaluación

Ocho fixtures nuevos, conocidos por el productor, con criterios fijados antes
de llamar a GLM: cuatro ausencias y cuatro controles positivos. Cubren método
general frente a específico, población objetivo frente a evaluada, coordinación
frente a autorización, cambio de objeto, negación explícita y cifras en conflicto.
Hay casos en inglés y español. No son un holdout ni una muestra representativa.

Corrida: `experiments/answer-scope-v1/runs/glm-01`. Código, entradas, criterios y
protocolo congelados. Máximo ocho llamadas, una por caso, GLM `glm-5.3-flash`,
temperatura 0, salida 8192 tokens, socket 90 s y proceso 110 s, sin reintentos.
Ninguna respuesta o criterio QASPER se incluye en los prompts de estos fixtures.
La línea base QASPER anterior se conserva intacta. No se ejecutó comparación
pareada legacy/concise: estos resultados no permiten cuantificar mejora causal.

## Autorrevisión adversarial

Riesgos residuales: explicación no sustentada; sobreabstención; respuesta breve
que pierda una excepción; métricas que premien brevedad a costa de contenido;
y generalización desconocida desde textos sintéticos cortos. Se preserva el
perfil anterior y no se cambia automáticamente el comportamiento de los usuarios.

Siguiente evaluación propuesta: fijar una nueva muestra QASPER sin artículos de
la primera batería y comparar ambos perfiles sobre las mismas preguntas, con
criterios y presupuesto congelados. Esta tanda de desarrollo no acredita mejora
sobre QASPER ni ahorro mediante recuperación; esas comprobaciones siguen pendientes.

## Resultado observado y correcciones del método

Primera tanda: 8 respuestas válidas, coincidencia de status 5/8 con criterios
congelados. D3/D5/D7 exponen una ambigüedad del propio diseño: el contrato permite
responder una ausencia explícita o límite de alcance, mientras el criterio exigía
abstención. No se cambian retrospectivamente esas etiquetas ni se presentan como
tres alucinaciones. Se construyeron cuatro casos nuevos de silencio inequívoco.

Segunda tanda: una llamada, rechazada por omitir quotes. Tercera: dos
abstenciones válidas y una salida rechazada por devolver una lista sin objeto
raíz; el cuarto caso no se ejecutó. Se precisó el ejemplo hasta mostrar el JSON
completo. No hubo reparación silenciosa ni reintentos automáticos.

Tanda final glm-04: 8/8 criterios satisfechos en desarrollo, cuatro abstenciones
y cuatro respuestas positivas, incluyendo negación explícita y conflicto 14/19
sin precedencia. Cuatro controles positivos se reutilizaron de la primera tanda.
No se observó sobreabstención en esos cuatro controles; no se generaliza.

Coste acumulado de las cuatro tandas: 20 llamadas, 22225 tokens reportados,
188.147 s sumados. La tanda final: 8714 tokens y 66.128 s.
Los fallos también se incluyen. No se calculó coste monetario.

180 pruebas locales pasaron. Verificados todos los freezes, hashes de
resultados y anclas; el código actual coincide con el de glm-04. Autorrevisión
contra fuentes y criterios: no independiente. En D4 la explicación menciona la
ausencia de escuelas urbanas, presente en fuente pero fuera de la cita elegida:
la cobertura de citas de la explicación sigue sin certificarse.

Evidencia completa: `experiments/answer-scope-v1/runs/review.json`.
La línea base QASPER conserva sus resultados anteriores y no fue reejecutada.

## Comparación posterior en artículos nuevos

[Resultados pareados](qasper-comparacion-perfiles-01.md): concise-v1 no se
promueve; sus respuestas son más cortas, pero tuvo dos rechazos, menos
abstenciones válidas y mayor consumo total. Legacy sigue por defecto.
