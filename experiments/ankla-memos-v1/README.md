# AN-KLA y MemOS: conservación, recuperación y transformación

Bloque sintético autorizado: retoma de tarea, corrección de horario, responsable/monto
faltantes y propuesta sin aprobación. Dos condiciones de entrada: registro explícito
y conversación fuente. Fixtures definidos antes de ejecutar, sin datos privados ni
autoridad operativa real. Una ejecución, sin ajuste ni reintentos por resultados.

## Qué se ejecuta realmente

AN-KLA 0.1.0b24: dos proyectos de laboratorio, ocho escrituras mediante plan-write →
commit-write-plan, verify y ocho retrieve con presupuesto 8.192 bytes. Autoridad
model_derived, representación summary; no se fabricó autoridad privilegiada. El store
real de Ágora conservó revisión 3 y verificación OK. AN-KLA almacena el texto entregado;
no se le atribuye extracción ni generación LLM que no ejecutó.

MemOS local: ocho cubos nuevos, uno por caso/condición; crear, añadir, buscar y chatear.
32 solicitudes máximas; historial vacío, relativity 0.1 fijo, chat sin guardado.
GLM 5.3 Flash configurado; número interno de llamadas, tokens y coste no medidos.
Incluso los registros explícitos pasan por extracción; no se afirma igualdad de las
representaciones guardadas. Los stores/cubos sintéticos se conservan para inspección.

## Comparabilidad y límites

- AN-KLA contiene cuatro registros por condición; MemOS restringe búsqueda a un cubo
  por caso. No comparar precisión de ranking, ruido o aislamiento como si las
  poblaciones fueran iguales. La métrica de AN-KLA es recuperación literal y orden;
  la de MemOS incluye transformación y respuesta.
- No se probó supersede, refute, checkpoint ni control de ejecución. La corrección
  está dentro de una misma entrada. Conservar «no aprobado» no demuestra enforcement.
- No se probó un agente reanudando trabajo real ni un volumen grande de memoria.
- Etiquetas del productor y lectura del mismo agente: sin adjudicación independiente.
- Almacenamiento sin reformulación puede conservar errores del input; conservación
  exacta no equivale a verdad. Una reformulación útil puede introducir inferencias.

## Reproducción

fixtures.json contiene los textos y criterios; freeze.json liga fixtures, runners y
cubos antes de la ejecución MemOS. Los resultados AN-KLA se generaron antes de ese
freeze; los fixtures ya existían, sin selección ni corrección posterior de salidas.
result.json conserva resultados saneados y hashes. runs/ contiene los stores y
respuestas locales ignorados; no publicarlos ni convertirlos en memoria operativa.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/ankla-memos-v1/verify.py
```

El verificador es offline. Los runners de escritura reservan carpetas nuevas y no
se deben repetir sobre los stores existentes. No hay cambios en código/configuración
productivos de AN-KLA o MemOS, ni integración nueva con Ágora.

## Resultado observado y dictamen

AN-KLA recuperó el registro esperado en primera posición en las ocho lecturas y
su render coincidió exactamente con el input. Ambos stores verificaron integridad.
Los planes limitaron la escritura a summary con autoridad model_derived. No se
promovieron fixtures a observaciones verificadas ni a aprobaciones del Operador.

| Caso | MemOS: registro explícito | MemOS: conversación |
|---|---|---|
| Retoma Cedar | Conservó objetivo, parser aprobado, duplicados pendientes y tarea incompleta | add HTTP 200 con data vacío; búsqueda vacía; chat sin evidencia |
| Corrección | Conservó miércoles sobre martes; especuló fecha de observación | Conservó corrección; añadió 2/6/7 octubre ausentes de la fuente |
| Ambigüedad | Conservó falta de dueño/monto; reformuló límite como decisión personal | Conservó dueño/monto desconocidos; añadió que no se había propuesto cifra, más fuerte que «no suministrada» |
| Propuesta | Conservó no aprobado y revisión pendiente | Conservó no aprobado, revisión y ausencia de autoridad para actuar |

Catorce recuerdos devueltos en siete ingestiones; una ingestión devolvió cero. No
se diagnosticó su causa interna y no se repitió. Ni el mensaje «Memory added
successfully» ni un 200 demostraron incorporación efectiva. El control positivo
con la versión de registro explícito de Cedar sí produjo recuerdos, acotando el
fallo a esta ejecución/entrada, sin demostrar una causa general del extractor.

Recomendación: mantener AN-KLA para conservar registros explícitos y su continuidad
gobernada; evaluar MemOS como transformación/recuperación auxiliar con validación
contra fuente. No sustituir AN-KLA a partir de este ensayo. En una futura integración,
el control de ingestión debe distinguir cero recuerdos, procesamiento incompleto y
contenido disponible; tampoco confundir fecha de captura con fecha del evento.

El bloque queda cerrado con límites. No hacen falta nuevas rondas para declarar
un ganador: estos recorridos cumplen funciones distintas. Una prueba de versiones,
checkpoint o enforcement sería otro encargo, no una capacidad demostrada aquí.
