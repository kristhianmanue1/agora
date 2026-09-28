# Corrección contractual local — 2026-09-28

**Implementada y probada como contrato experimental separado; no activada en los
consumidores existentes.** Cero llamadas nuevas a modelos.

El replay usa las respuestas preservadas de partial-selection-v2 y la entrada
exacta enviada a cada evaluación, exportadas como fixtures sintéticos. Verifica
hash del contenido original, preserva fields/reason y añade explícitamente schema
y reviewed_scope mediante el adaptador del host. No atribuye esos campos a GLM.

| Respuesta histórica | Resultado bajo v3 | Nueva representación v4 |
|---|---|---|
| Ausencia sin antecedente | Rechazada: missing_evidence | partial, date=missing, evidence=[] |
| Contradicción | Candidata partial | partial, date=disputed, ambas citas conservadas |

Los resultados históricos no cambian. La aceptación v4 es una comprobación local
de una nueva representación, no una nueva respuesta GLM ni prueba de que un
modelo emitirá el nuevo contrato. Los requests y sus hashes originales se
conservan como procedencia; el prompt v4 aún no fue ejercitado con proveedor real.

## Pruebas y autorrevisión adversarial

371 pruebas pasan, incluidas 16 nuevas. Casos negativos: alcance ausente, fuente
alterada, versión/identidad/localizador/offset falsos, confusión booleano-entero,
citas de metadatos, valor afirmado como missing y evidencia vacía para supported,
disputed o withdrawn. Control positivo: ambas respuestas históricas se reproducen
manteniendo íntegros sus campos y explicación.

Hallazgo durante revisión: comparar diccionarios Python aceptaba True como 1;
la comparación de representación JSON distingue esos tipos. Se añadió regresión.
No hubo revisor independiente.

Riesgos residuales: supplied_input_only prueba relación con el input, no atención
cognitiva, exhaustividad, autenticidad ni ausencia global. La validez literal no
acredita que una cita respalde el valor o que dos citas se contradigan. Un caller
que sustituya también el input cambia el objeto validado; no se añade firma.

## Adopción pendiente

issue-store-v1, issue-recovery-v1 y sus historiales permanecen con v3, sin cambios
ni migración. Próximo paso propuesto: un consumidor versionado que persista v4 y
el alcance, pruebe recuperación tras reinicio y rechace reinterpretar bases v3.
Primero pruebas locales con estos fixtures; no requiere otra llamada GLM.
