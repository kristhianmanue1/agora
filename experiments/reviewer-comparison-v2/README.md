# Revisores: AttrScore reservado y documentos grandes

Protocolo fijado antes de llamadas, 2026-09-28. GLM sigue siendo el generador
configurado; aquí sólo se comparan revisores. No se cambia ningún predeterminado.

## Selección

- 24 casos AttrEval-GenSearch originales, 8 por clase. Semilla fija, exclusión
  por pregunta, respuesta O referencia normalizada de los 36 casos previos y
  dentro de la selección nueva. Revisión y hashes en selection.json.
- Etiquetas externas sin cambiar: Attributable→supported,
  Contradictory→contradicted, Extrapolatory→insufficient. El mapeo puede producir
  desacuerdos taxonómicos: concordancia con gold no equivale a verdad adjudicada.
- 12 controles sobre dos documentos QASPER no utilizados en pilot-01, pilot-02
  ni large-source-v1: 1811.00051 (116094 bytes) y 1911.03977 (68344 bytes).
  Selección deliberada de textos largos sobre generación y modelos multimodales;
  no muestreo representativo ni selección ciega respecto al contenido.
- Tres afirmaciones por documento, cada una contra el texto completo y contra
  su abstract. Los criterios de estas 12 variantes son del productor, contrastados
  con párrafos del texto; no son etiquetas oficiales QASPER ni revisión independiente.
  Esta segunda batería mide respaldo condicionado al alcance, no calidad de un
  resumen global ni exhaustividad de recuperación.
- No se mezclan métricas AttrScore con controles propios ni full con abstract.
  Reservado significa no usado en pilotos locales, no ausencia en entrenamiento.
  Documentos y fuentes siguen en inputs/ ignorado; metadatos permiten reproducir.

## Contrato y ejecución

Se reutilizan instrucciones, criterios, transporte y parser congelados del piloto
v1. Ambos reciben el mismo JSON de question/evidence/claim. Se añade question
porque las respuestas externas pueden depender de ella; no se envía gold.
GLM: glm-5.3-flash, temperatura 0, JSON, máximo 2048 tokens de salida.
Jev: jev-1.13.0, choice. Una llamada por caso/proveedor: máximo 72 en esta tanda,
90 s por llamada, cero reintentos. Hasta 73728 tokens de salida GLM (no presupuesto
monetario ni total); la entrada incluye documentos completos y se mide por separado.
Parada por proveedor ante 401/402/403/429 o tres errores. Las solicitudes fallidas y
no ejecutadas permanecen en el denominador. No truncar automáticamente ni reducir
texto después de un rechazo de contexto. No repetir casos para mejorar resultados.

Jev documenta 32k tokens para state+pregunta más larga y 64k por petición; un texto
en bytes no acredita estar dentro del límite. Un rechazo será limitación observada,
no respuesta semántica. Precio consultado: USD 0.042 por millón de tokens de entrada,
salida gratuita; una estimación con esta tarifa no verifica cargos del ledger.
Fuentes: https://docs.typesafe.ai/models y https://docs.typesafe.ai/api.

## Métricas y regla de decisión

Concordancia, matriz de confusión, macro-F1 y falsa aceptación respecto al gold;
fallos explícitos, tokens, latencia y comparación pareada en los mismos casos.
En full/abstract comprobar que una ausencia en el abstract no se confunda con una
negación en el documento. Publicar todos los resultados, también desfavorables.
No promover automáticamente con esta muestra pequeña y una repetición por caso.
Un desacuerdo material de autoridad, evidencia o alcance requiere análisis antes
de recomendar sustitución. La estabilidad entre repeticiones queda pendiente.

## Reproducción

Preparación con corpus locales verificados: PYTHONPATH=src python3
experiments/reviewer-comparison-v2/prepare.py. Rechaza inputs existentes.
run.py usa Llavero como en v1 y exige --out nuevo; nunca lee gold.json.
freeze.json fija hashes antes de llamar. records-*.jsonl conserva respuestas finales
sin repetir el contenido documental; cada registro identifica la petición por hash.
