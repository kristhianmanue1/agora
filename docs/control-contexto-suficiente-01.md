# Control con contexto suficiente: dos fallos de entrega y una discrepancia local

2026-09-23. Ensayo de una llamada completado; resultado rechazado.
Evidencia: `experiments/large-source-v1/runs/sufficient-01` (local, fuera de Git).

## Método y resultado

Se seleccionaron explícitamente seis párrafos originales que respaldan los seis
criterios G1: métodos de nombres/planes, selección humana, evaluación y límite
automático, recursos manuales comunes, e idiomas. Se conservaron los bytes y
se fijó el mapa criterio→párrafos antes de llamar. Total: **6965 bytes**, dentro
de 12000. Selección del productor usando referencias conocidas: control de
síntesis, no éxito de recuperación automática ni evaluación independiente.

Mismos pregunta, consumidor passage_cli, prompt base, modelo solicitado/reportado
`glm-5.3-flash`, temperatura 0, máximo 8192 tokens; formato proveedor omitido;
timeout socket/proceso 180/200 s. Una llamada, sin reparación ni reintento.
Consumo: **5104 tokens**, 47.367 segundos. Terminó con `stop`, JSON parseable,
pero fue rechazada con `invalid_answer_shape`.

## Hallazgos de autorrevisión

1. **15 citas frente al máximo local de 12.** El validador rechaza la forma antes
   de verificar literalidad. No se recortó la lista para hacerla pasar.
2. **Una cita no literal.** La primera cambia `INLINEFORM1` por `INLINEFORM0`.
   Las otras 14 aparecen literalmente dentro de los pasajes suministrados.
   Comprobación local posterior del productor; ninguna se convirtió por ello
   en una cita aceptada del resultado rechazado. Una modificación pequeña de un
   marcador sigue siendo una modificación de evidencia.
3. **Discrepancia entre prompt y validador.** El prompt base de `query.py`, usado
   por passage_cli, pide citas exactas pero **no comunica el máximo de 12**.
   El consumidor routed_query sí añade ese límite explícito, pero no se usó en
   este control. No atribuir el exceso exclusivamente a desobediencia del
   proveedor: el sistema no le comunicó esa restricción. El defecto observado
   no implica que comunicarla baste para garantizar su cumplimiento.
4. **Cobertura no equivale a fidelidad completa.** El texto bruto menciona los
   seis criterios, incluidos los recursos manuales comunes y el fracaso de
   automatización total antes omitidos. Sin embargo, dice que el clasificador
   «puntúa hasta 5 candidatos», cuando la fuente dice que puntúa candidatos para
   identificar los mejores, hasta cinco. Confunde puntuación y selección.
   No se certifica fidelidad perfecta ni se cuenta la salida como aceptada.

## Qué demuestra

Disponer de evidencia suficiente permite que esta respuesta mencione los aspectos
antes perdidos; aun así, la entrega falla por exceso de citas y alteración de una
cita. La selección no es el único cuello de botella. No demuestra que toda
síntesis con esa evidencia falle, ni que otra configuración funcionaría.

Hashes de código, entradas, protocolo y respuesta verificados; código vigente
idéntico al congelado. Los seis rangos coinciden con los párrafos originales y
respetan el presupuesto. Auditoría reproducible: `audit_sufficient.py`.
No se modificó producto ni se repitió su suite. Sintaxis de scripts y
`git diff --check` comprobados. Revisión del mismo productor, no independiente.

## Próximo incremento recomendado

Corregir primero la discrepancia local: declarar el límite de citas en el prompt
base desde la misma constante que usa el validador y comprobar los límites 12/13.
Conservar el rechazo estricto y la evidencia anterior. Después ejecutar una sola
regresión del control congelado, identificada como versión nueva del prompt.
No aumentar el máximo ni eliminar citas para aceptar retrospectivamente fallos.

Si persisten citas modificadas, el siguiente diseño a evaluar será devolver
identificadores de unidades de evidencia suministradas y resolver el texto
literal localmente. Eso requiere contrato versionado y pruebas; un identificador
válido tampoco demuestra que la evidencia respalde la afirmación.

El selector por aspectos queda sin promoción mientras no se separen cobertura,
fidelidad semántica y validez de entrega. No lanzar otra campaña amplia todavía.
