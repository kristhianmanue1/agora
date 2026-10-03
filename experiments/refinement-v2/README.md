# Referencias por identificador y reparación explícita — 2026-10-03

## Estado: implementación verificada; reparación funcional parcial

El consumidor `passage_cli` incorpora `--citation-mode ids` (contrato v0.4
optativo), reutilizando las unidades y validación existentes. El modelo elige IDs;
el código resuelve citas literales y localizadores. `literal` sigue predeterminado.
Hay límites verificados de seis afirmaciones, cuatro faltantes y 2.000 caracteres
sumados de texto generado. Se conserva el control de alcance y no hay admisión ni
reparación automática. `--reasoning-effort` es otra opción explícita y registrada.

## Pruebas reales y coste (todos los intentos incluidos)

| Caso | Ajuste | Resultado | Tokens |
|---|---|---|---:|
| Etiquetado de satisfacción | IDs, esfuerzo omitido | Rechazado: generación incompleta | 16 280 |
| Mejora del rendimiento | IDs, esfuerzo omitido | Candidato con cifras y condiciones recuperadas | 14 363 |
| Etiquetado de satisfacción | IDs, esfuerzo low | Rechazado: presupuesto de citas excedido | 12 891 |
| Total | Tres llamadas, sin reintentos automáticos | Una candidata, dos rechazos | 43 534 |

Los dos primeros intentos se congelaron juntos. Tras observar el truncamiento,
se congeló una prueba adicional separada con `low`; no se borra ni reemplaza el
resultado anterior. Preguntas y documentos ya conocidos: no es validación reservada.
Los 43.534 tokens son adicionales a los 45.829 de refinement-v1; no son ahorro.
No hubo llamadas nuevas a MemOS o Jev, ni medición monetaria/infraestructura.

### Caso recuperado

La respuesta de rendimiento conserva hasta 9,4 puntos de accuracy / 31% en el
conjunto pequeño, 1,6 con 131k ejemplos y diferencias F1 de 0,28 / 0,42 con 1k.
Los IDs se resuelven a segmentos exactos y las cifras se contrastaron con la fuente
por el productor. Permanece candidata y `semantic_support: not_verified`.

### Caso pendiente

Con configuración predeterminada, el proveedor reportó los 4.096 tokens de salida
consumidos en razonamiento. Acotar el texto no limita el razonamiento interno.
Con `low`, la respuesta terminó, pero acumuló **22.426 bytes de citas** frente al
límite de 12.000, incluyendo unidades largas y evidencia repetida entre afirmaciones.
El consumidor la rechazó; no se relajó el presupuesto para obtener un pase.

La inspección semántica encontró además que inventó el umbral positivo «3 en
adelante» donde el texto QASPER sólo contiene `INLINEFORM0`, pese a la instrucción
de no reconstruir fórmulas. Añadió una discusión del apéndice con un mapeo
internamente contradictorio. Ese defecto lo identificó el productor; **el gate
estructural no acredita detectarlo**. `low` no se promueve como configuración
recomendada. Una cita exacta puede acompañar una afirmación sin respaldo.

La [documentación oficial de Z.AI](https://docs.z.ai/guides/capabilities/thinking),
consultada el 2026-10-03, permite low/high/max para GLM-5.3/Flash y prohíbe desactivar
thinking en esos modelos. Configuración solicitada no prueba grado interno efectivo;
el receipt sólo conserva uso y modelo reportados, sin contenido de razonamiento.

## Verificación y autorrevisión adversarial

543 pruebas locales pasan: ocho nuevas de IDs/UTF-8, faltantes, alcance, límites,
IDs inválidos/duplicados y truncamiento; dos nuevas del transporte (envío/registro
de low y omisión compatible). Se validaron contra bytes originales las unidades y
anclas de citas del candidato real. Contratos anteriores conservan sus pruebas.

La autorrevisión comprobó compatibilidad optativa, rechazo sin salvamento, costes
incluyendo fracasos y separación entre procedencia y fidelidad. No participó un
revisor independiente. El hash de implementación de cada intento está conservado;
la opción de esfuerzo se añadió entre default y low, documentada en cada freeze.
Los receipts omiten prompt y fuente íntegra; se conserva su identidad SHA-256.
Los ejecutores mantienen rutas del laboratorio original y requieren fuentes
fijadas y Llavero; no contienen credenciales.

## Continuación acotada

No abrir más documentos todavía. Convertir el caso de fórmula ausente en una
regresión semántica y evaluar una selección de evidencia más enfocada, conservando
faltantes explícitos. El cierre funcional exigirá respuesta útil sin inventar el
umbral y sin relajar presupuestos. El caso de cifras ya no necesita otra llamada.
