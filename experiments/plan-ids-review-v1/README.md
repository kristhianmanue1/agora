# Revisión semántica del plan por IDs

## Protocolo congelado

Seis afirmaciones reales del Manual DPM, con evidencia resuelta por IDs, y seis
casos AttrScore nuevos: dos por clase. El revisor recibe sólo pregunta,
afirmación y evidencia; gold se conserva separado. Selección determinista,
excluyendo 60 casos previos por pregunta, respuesta O referencia normalizada.
Reservado localmente no implica ausencia en entrenamiento ni independencia
semántica entre casos. No se mezclan resultados del manual y AttrScore.

Evaluación propuesta: Jev con transporte/prompt/parser de reviewer-comparison-v2,
máximo doce llamadas, timeout 90 s por llamada, cero reintentos; detener ante
401/402/403/429 o tres errores. Errores y no ejecutados permanecen en denominador.
No cambiar prompt ni casos tras resultados; no promover revisor automáticamente.

## Revisión local del productor

Se cotejaron las seis afirmaciones ya generadas con las unidades resueltas y
sus offsets en el texto fijado. Las doce citas coinciden con la fuente.

| Área | Contraste | Resultado local |
|---|---|---|
| Atención Médica | Políticas/programas y autorización previa del titular | Respaldada; conserva condición de autorización |
| Educación e Investigación | Profesionalización y evaluación de competencias | Respaldada; conserva colectivos y finalidad |
| Planeación e Innovación | Normas, tecnología/inteligencia, insumos y vigilancia | Respaldada en los fragmentos |
| Infraestructura | Servicios indirectos/subrogados y planeación de infraestructura | Respaldada; conserva alcance institucional |
| Proyectos Especiales | Normatividad sobre gestión de riesgo de desastres | Respaldada en el fragmento |
| Servicios Administrativos | Coordinación de recursos con órganos institucionales | Respaldada; no transforma coordinación en autoridad exclusiva |

La revisión es del mismo productor, **no independiente**. Cada afirmación
presenta una responsabilidad, no una lista exhaustiva. La salida conserva dos
faltantes: organigrama completo y vigencia externa. No se verificó vigencia legal
ni clínica. La respuesta es extensa y reproduce frases: el respaldo local no
acredita una buena compresión. Algunos entrecomillados de la prosa normalizan
espacios; las citas canónicas son las resueltas en `quotes`, con offsets originales.

## Ejecución externa completada

Autorización explícita posterior del Operador: doce llamadas a Typesafe/Jev,
cero errores, cero reintentos. El bloqueo previo se resolvió por autorización,
no mediante cambio de destino ni elusión. Resultados en [RESULTS.md](RESULTS.md).

Entradas y corridas permanecen en `inputs/` y `runs/`, ignorados por Git.
`freeze.json` identifica entradas y etiquetas; `selection.json` registra exclusión
y corpus; `cases-metadata.json` conserva procedencia sin publicar el texto privado.
La preparación reutiliza el selector anterior y no modifica código de producto.
