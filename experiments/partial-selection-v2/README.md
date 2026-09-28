# Ausencia sin antecedente y contradicción — v2

Dos casos sintéticos independientes, sin evaluación previa ni estado sembrado:

- Ausencia: sólo llega «Lina es responsable de Nube». La fuente completa contiene
  una fecha en otro segmento; el modelo no recibe ese segmento ni una declaración
  de fecha pendiente. Debe devolver fecha null/missing y responsable Lina.
- Conflicto: dos fuentes del mismo día y coordinación declaran fechas distintas
  para Nube (21 y 28 de octubre). Ninguna declara sustituir a la otra. Debe
  devolver fecha null/disputed, citar ambas y conservar responsable Lina.

Ambos deben quedar partial. Las explicaciones se revisan por el productor: no
inferir ausencia global ni decidir prevalencia por orden de presentación. El
caso positivo de ampliación está en v1; aquí no se añade otra llamada equivalente.

Se conserva el prompt v1 sin añadir instrucciones que revelen las respuestas.
Gold, inputs, presupuesto y hashes se fijan antes de llamar. Máximo dos llamadas,
8192 tokens de salida/call, 180 segundos HTTP, cero reintentos. Sólo GLM mediante
Llavero; ninguna fuente real. Los dos casos empiezan en frío para excluir ayuda
de una evaluación previa. Por eso no prueban el flujo incremental de recovery-v1.
SQLite conserva candidatos, fuentes y requests; transporte incierto no se reenvía.
El runner exige una carpeta nueva y no implementa reanudación automática.

Revisión estructural, valores y citas literales no garantizan semántica. Un caso
por variante no estima robustez, ahorro o superioridad. No hay admisión ni watcher.
