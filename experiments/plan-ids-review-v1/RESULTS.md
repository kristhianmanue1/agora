# Revisión Jev del candidato por IDs y seis casos reservados

## Resultado

Doce llamadas autorizadas completadas, sin errores ni reintentos. Modelo
reportado por API: `jev-1.13.0`. El transporte no recibió gold: se verificó el
contenido de `state` contra pregunta, afirmación y evidencia congeladas.

| Grupo | Resultado | Entrada/salida reportadas | Tiempo acumulado |
|---|---|---|---|
| Manual DPM, 6 afirmaciones | 6 supported; coincide con el cotejo del productor | 3.820 / 264 tokens | 2,300 s |
| AttrScore reservado, 6 casos | 4/6 coincidencias con etiquetas originales; macro-F1 0,667 | 3.328 / 279 tokens | 2,172 s |

Evidencia: [result.json](result.json). Contiene etiquetas, respuestas tipadas,
uso, tiempos y hashes de peticiones; excluye fragmentos del manual. Inputs y
registros completos quedan locales. Total reportado: 7.691 tokens. No se estima
coste monetario ni se atribuye la confianza del proveedor a calibración validada.

## Desacuerdos conservados

- `reserved-189`: gold supported, Jev insufficient. La afirmación fija una edad
  al ganar y el año 2018. El fragmento establece edad actual de 19 años y una
  victoria el año anterior, sin fechar la publicación. No permite derivar sin
  supuestos la edad al ganar ni el año absoluto. El dictamen de Jev es defendible
  bajo la rúbrica estricta usada aquí.
- `reserved-55`: gold contradicted, Jev insufficient. La afirmación habla de la
  mayoría de los huevos de ganso en 28–32 días; la evidencia da un rango posible
  de 28–35. No se deriva la distribución de frecuencias ni una contradicción
  explícita de “la mayoría”. También es defendible la abstención del revisor.

Estas interpretaciones son del productor. **No se cambiaron las etiquetas ni se
recalculó una puntuación corregida de 6/6**. No hubo adjudicador independiente.
Los desacuerdos pueden reflejar límites de información y diferencias entre el
criterio de etiqueta externo y el contrato estricto, no un fallo demostrado del
modelo en ambos casos.

## Qué queda demostrado y qué no

El flujo produjo referencias exactas y seis afirmaciones respaldadas según el
cotejo local y el revisor externo. Eso no acredita ausencia de omisiones del PDF,
exhaustividad del organigrama, vigencia externa ni generalización. Las seis
responsabilidades del manual son un solo documento y todas las etiquetas son
positivas: no miden por sí solas capacidad de detectar errores.

En los cuatro casos reservados con gold no-supported no hubo falsa aceptación
como supported; es una muestra demasiado pequeña para estimar seguridad o tasa
general. No se ejecutó una comparación pareada con GLM ni repeticiones; no se
recomienda sustituir el revisor predeterminado.

El revisor recibió el texto resuelto de las referencias, no tuvo que interpretar
los IDs. La validación de identidad y offsets pertenece a Ágora. La respuesta
original permanece candidate_partial, semantic_support=not_verified: este
informe no modifica ni admite la revisión original automáticamente.

## Recomendación

Mantener IDs como opción y Jev como revisor opcional. La siguiente evaluación
útil debe incluir controles negativos del mismo dominio: responsabilidad
atribuida a otra área, pérdida de autorización previa y ampliación indebida de
alcance. Congelarlos antes de medir, separados de AttrScore. Adjudicar los dos
desacuerdos antes de usarlos para ajustar prompts. No aumentar indiscriminadamente
la batería ni convertir coincidencias de modelo en autoridad.

Sin cambios de código de producto. Se verificaron hashes congelados, separación
de gold, las doce respuestas y métricas. La suite de 460 pruebas corresponde al
código previo, no se repitió para este registro documental. Publicación no implica
admisión en AN-KLA ni despliegue.
