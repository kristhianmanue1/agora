# Tres pasos: batería, publicación de Skopos y recorrido conjunto

## 1. Batería ampliada de Ágora

Doce casos nuevos, seis pares, tres en español y tres en inglés. Fecha, sujeto,
atribución sin verificar, excepción, incertidumbre y combinación de dos fragmentos.
Mismos prompts que antes; gold fijado antes de ejecutar. GLM solicitado/reportado:
`glm-5.3-flash`. 36 solicitudes completas, sin reintentos ni consumo desconocido.

| Métrica | Combinada v1 | Separada v1 |
|---|---:|---:|
| Casos completos | 12/12 | 12/12 |
| Respaldo correcto | 12/12 | 12/12 |
| Pertinencia correcta | 11/12 | 12/12 |
| Ambos ejes correctos | 11/12 | 12/12 |
| Pares completamente correctos | 5/6 | 6/6 |
| Casos en español correctos | 6/6 | 6/6 |
| Casos en inglés correctos | 5/6 | 6/6 |
| Solicitudes | 12 | 24 |
| Tokens totales reportados | 15535 | 15466 |
| Suma de duración por caso | 223.563 s | 211.599 s |

Fallo concreto de la combinada (2-on): «Vela shipped 20 units», pregunta por Vela,
cita sobre Orbe. El respaldo correcto es insufficient y la pertinencia relevant;
la combinada marcó extra. La falta de evidencia sobre Vela no vuelve ajena la
respuesta a la pregunta por Vela. La separada conservó ambos ejes correctamente.

31 001 tokens totales, sin cálculo monetario ni confirmación de factura. Diferencia
de consumo de sólo 69 tokens; no se concluye ahorro relevante. La separada necesitó
el doble de solicitudes, y una de respaldo tardó 51.5 s. Duración y consumo dependen
de salida, caché y variación del proveedor. Un acierto no elimina ese coste operativo.

Evidencia publicable en `experiments/split-comparison-v2/`: casos, gold, protocolo,
ejecutor, auditor, scorer y resultados por caso. Artefactos crudos locales ignorados
en `runs/glm-01/`. La auditoría valida integridad local, no identidad del proveedor.

## 2. Skopos publicado

Commit `5773dbd8b6440f8ddb44d334f56f7fb98fa91ad0`, rama
`codex/meeting-source-currency`, SHA remoto confirmado. El árbol quedó limpio.
No se fusionó con main: la rama nace de la documental pendiente `93b4b79`, por lo
que la revisión de una eventual fusión debe considerar también esa ascendencia.

Incluye corrección de búsqueda que resucitaba versiones antiguas; pruebas de
regresión contra Mongo de test; aislamiento corregido de un test; actualización
documental de P-007; piloto de reuniones, persistencia SQLite y exportación de
fragmentos verificados. No se reindexó el corpus ni se desplegaron servicios.

Suite final: 305 pruebas, una omitida, sin fallos. Se bloqueó selección de bases
Mongo distintas de admin/skopos_test*. Gate de tamaños OK (144 archivos); gate de
planes inactivo. Una corrida previa contó pruebas heredadas duplicadas; se eliminó
esa duplicación antes de informar el conteo final. El piloto es experimental y su
SQLite no sustituye el almacenamiento de producción de Skopos.

## 3. Recorrido conjunto

Protocolo en `experiments/meeting-bridge-v1/README.md`: fuente sintética con revisión
lunes→martes, dos fragmentos, fecha/cantidad y responsable/condición, presupuesto
no informado. Persistencia y reapertura, recuperación vigente, exportación,
entrada local de Ágora, generación y revisión separada. Tres solicitudes como
máximo, sin reintentos; no hay escrituras AN-KLA ni acceso al corpus de producción.

La prueba previa con proveedor simulado comprueba el cableado y la navegación,
no exactitud de GLM. Sus resultados están separados de la ejecución real.

### Resultado real del recorrido — parcial

Skopos reabrió la base, recuperó revisión 2 y excluyó lunes. GLM recibió esa fuente
verificada y respondió en 17.218 s, 1744 tokens reportados. La respuesta terminó
con finish_reason=stop pero su JSON estaba mal cerrado en la lista missing:
Ágora la rechazó con invalid_json. No se ejecutaron los dos revisores, no hay citas
admitidas ni adjudicación. Una solicitud real, sin reintentos; los artefactos
simulados se conservan separados y no cuentan como respuestas GLM.

La lectura del texto bruto permite observar martes 29, 40 equipos, Nerea, prueba
de aceptación y ausencia de presupuesto. Eso no transforma la salida inválida en
candidato válido. No se reparó el JSON ni se publicó una respuesta como aceptada.
La auditoría verificó las entradas congeladas y la fuente; el recorrido semántico
de extremo a extremo queda pendiente. Archivo público: meeting-bridge-v1/result-glm-01.json.

Se detectó y corrigió un defecto del ejecutor experimental: devolvía exit code 0
cuando el proveedor respondía pero Ágora rechazaba el candidato. Ahora ese caso
devuelve 2 y no invoca revisores. Un control nuevo con proveedor simulado malformado
comprobó ambas propiedades; no se volvió a llamar a GLM. La corrida original
conserva su código y resultado originales. Esta corrección no acredita éxito de
la generación ni altera la evidencia anterior.

En total, este bloque consumió 39 solicitudes como techo y ejecutó 37 reales:
36 de comparación y una del recorrido. Tokens reportados: 32745. No hay consumo
real atribuible a los proveedores simulados ni costes monetarios calculados.

## Evaluación adversarial y continuación

Autorrevisión, sin revisor independiente. Seis pares nuevos siguen siendo pocos;
idioma y mecanismo no están cruzados exhaustivamente, sólo una ejecución por caso.
Los prompts difieren además de la separación: no atribuir causalidad a ésta sola.
Los controles revisan afirmaciones suministradas; no miden por sí solos omisiones
en respuestas libres. El recorrido conjunto comprueba una tarea con hechos conocidos.

Conservar la revisión separada como optativa. Antes de promoverla: casos nuevos de
mayor extensión, repetición, fuentes con excepciones/atribución y evaluación de
omisiones; una muestra real autorizada para el conector de reuniones. No convertir
publicación de rama, hashes, citas literales o etiquetas GLM en adjudicación.

Prioridad siguiente: resolver la salida estructurada del generador con una
comparación acotada (p. ej., modo de referencias por ID ya existente), conservando
rechazos y sin reparación silenciosa. El piloto conjunto está parcial; no se
promueve a integración validada por las pruebas de transporte o recuperación.
