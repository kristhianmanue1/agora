# Ensayo con documento real: la ruta compleja no siempre conviene

## Conclusión

En una propuesta real de 15 826 bytes de texto y seis tablas, la lectura completa
consumió menos tokens y produjo dos respuestas aceptadas por el contrato. El
recorrido más consulta produjo una respuesta aceptada y una rechazada, con más
del doble de tokens. Esto respalda elegir la ruta según tamaño y presupuesto;
no demuestra que la lectura completa sea universalmente superior.

El DOCX aportado permanece intacto. Se extrajeron párrafos y tablas por OOXML,
con filas y columnas delimitadas; no había imágenes, revisiones, notas ni texto
en cuadros. No se verificó paginación o presentación mediante render. Los anclajes
corresponden al texto extraído, vinculado por SHA-256 al original, no a páginas Word.
Documento, preguntas detalladas y resultados permanecen excluidos de Git.

## Método

Dos preguntas fijadas después de leer el documento y antes de las llamadas:
Q1, plan e importes de todas las etapas y estado del presupuesto;
Q2, discrepancias entre una tabla de esfuerzo y títulos de apartados.
No hubo cegamiento ni conjunto independiente. Se contrastaron respuestas y citas
con fuente y referencia congeladas mediante autorrevisión adversarial del productor.

`glm-01` se detuvo en Q1 directa: consumió 2048 tokens de salida y terminó por
límite, sin respuesta completa. Rechazo conservado, 6545 tokens totales.
En `glm-02` sólo se elevó la salida máxima a 8192. Se mantuvieron preguntas,
criterios, modelo `glm-5.3-flash`, temperatura 0 y socket 90 s. El proveedor reportó
el modelo configurado; eso no lo verifica independientemente.

El recorrido utilizó cuatro unidades de 4096 bytes, con vecinas de contexto,
cuatro llamadas máximas, 65536 bytes de prompt acumulado y 8192 bytes de citas
retenidas. Ambas consultas usaron presupuesto de prompt de 32768 bytes. La fuente
completa cabe en ese presupuesto. Un intento fallido no se reinterpretó como éxito.
Tras el rechazo de Q1 por citas se continuó sólo con Q2, no intentada; se registró
esa continuación y no se repitió Q1. Trece llamadas totales entre ambos ensayos.

## Resultados de glm-02

| Caso y ruta | Tokens | Segundos | Resultado |
|---|---:|---:|---|
| Q1 completa | 9685 | 66,858 | Aceptada; cubre plan, importes y borrador, con matiz de fidelidad |
| Q1 recorrido + respuesta | 23603 | 153,359 | Rechazada por 16 citas; límite 12. Además omite componentes |
| Q2 completa | 6861 | 36,910 | Aceptada; conserva discrepancias |
| Q2 recorrido + respuesta | 18328 | 102,289 | Aceptada; conserva discrepancias |
| Total completa | 16546 | 103,768 | Dos respuestas aceptadas |
| Total recorrido + respuesta | 41931 | 255,648 | Una aceptada y una rechazada |

Los tokens incluyen razonamiento reportado por proveedor y no equivalen a coste
monetario. Caché, orden y latencias no estuvieron controlados. El ensayo comparativo
sumó 58477 tokens; con el rechazo inicial, 65022. Se verificaron 20 archivos congelados
y 6 resultados de glm-02 por hash y las citas aceptadas contra el texto fuente.
No se modificó código del producto ni se reejecutó su suite en este encargo.

### Hallazgos de fidelidad

**Q1 directa:** los criterios principales están presentes. Sin embargo, añade cifras
de meses-persona tomadas de la tabla y no advierte sus discrepancias con los títulos.
Aceptación estructural no significa fidelidad perfecta.

**Q1 por fragmentos:** devuelve 16 citas donde se admiten 12. No se amplió el contrato
para aprobarla. Al revisar el texto bruto también se observa pérdida semántica:
resume la primera etapa sólo como despliegue y soporte, aunque los demás componentes
sí aparecen en la evidencia retenida. La pérdida ocurrió en síntesis. Elevar el
límite de citas no corregiría esa omisión. Los 16 extractos brutos son literales en
el original, pero eso no vuelve completa la respuesta.

**Q2:** ambas rutas preservan los dos pares de cifras contradictorias, identifican
tabla y apartados, y no eligen una versión. Se conserva la contradicción documental
sin convertirla en decisión del proyecto ni corregir el Word.

## Decisión recomendada

1. Priorizar lectura completa si cabe en el presupuesto de contexto, reservando
   salida suficiente. El presupuesto de entrada y el de salida son distintos.
2. Mantener recorrido para fuentes que no caben o tareas que justifiquen su coste;
   no imponerlo a documentos pequeños.
3. Antes de promover síntesis global, descomponer la solicitud en partes verificables
   y evaluar omisiones por parte. Comprobar tanto límite de citas como significado.
4. Repetir la comparación con más documentos y preguntas nuevas antes de adoptar
   un umbral de selección como política general.

Estas son recomendaciones; no se implementó un selector de rutas ni se modificó
el contrato de citas. No hubo commit, push, escritura en memoria ni cambios de
contexto canónico. La ejecución evalúa fidelidad al borrador, no veracidad externa
de sus afirmaciones ni validez clínica, legal o presupuestal.

Evidencia reproducible local: `experiments/real-document-v1/inputs/` y
`experiments/real-document-v1/runs/glm-01/`, `runs/glm-02/`.

## Incremento posterior

La [selección de ruta y respuestas por partes](seleccion-ruta-y-partes.md) incorpora
estas recomendaciones en una CLI nueva. La regresión guiada recuperó los componentes
omitidos; los rechazos de este ensayo no se modificaron ni reclasificaron.
