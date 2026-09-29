# Recuperación real y revisión de suficiencia

## Protocolo ejecutado

Dos documentos públicos ya usados en el diagnóstico; ahora son casos de desarrollo, no reservados nuevos. Se usó `agora.qasper.render` (párrafos con doble salto) y `agora.passages.prepare(mode=retrieve)`, presupuesto fijado de 8.000 bytes, top_k=3, sin fallback ni cambios de consulta después de observar recuperación. Al recuperador sólo llegaron fuente y pregunta original: ni anotaciones de evidencia, ni respuesta, ni gold.

El render anterior del piloto de revisión tenía un salto entre párrafos. Los hashes son distintos; se verificó igualdad del texto salvo espacios. No se fingen offsets compatibles entre serializaciones. Los rangos de este piloto son bytes UTF-8 sobre el render actual. El corpus QASPER de origen conserva su hash.

Cuatro candidatos fijos (dos por documento), sin nueva generación, se revisaron con GLM y Jev: ocho llamadas, 90 s/caso, cero reintentos. El transporte, prompt y ejes son los del diagnóstico anterior. `source_sufficiency` es un juicio del modelo, no garantía de cobertura de todo el documento.

## Resultado

Ágora recuperó 3.786 de 51.936 bytes en el primer documento y 5.254 de 64.497 en el segundo. Las referencias se comprobaron contra los bytes exactos. En el primero aparece el párrafo que distingue evaluación entity-typing y entrenamiento Wikipedia; no se recuperaron los dos párrafos que mencionan denoising. En el segundo aparece la lista explícita de cinco idiomas.

Ambos revisores produjeron los mismos juicios: r01 y r02 omitted, r03 complete, r04 omitted; los cuatro contextos recibieron source_sufficiency=sufficient. El primero permite refutar la completitud del candidato sobre Wikipedia, pero no permite afirmar que se hayan cubierto todas las evaluaciones. El acuerdo entre modelos no cierra ese hueco.

Ver [resultados](result.json), [recuperación](retrieval.json) y [auditoría posterior](coverage-audit.json). No se hereda gold de otro contexto: no se publica una supuesta precisión 4/4.

## Medición

| Revisor | Entrada | Salida | Segundos de solicitudes | Reducción entrada frente a documento completo previo |
|---|---:|---:|---:|---:|
| Jev | 6.067 | 379 | 1,457 | 88,72% |
| GLM | 4.708 | 1.515 | 30,259 | 90,54% |

Total del lote: 12.669 tokens reportados, ocho llamadas sin errores ni reintentos. Recuperación local: unos 0,0084 s; escanea el texto completo localmente (116.433 bytes entre ambos documentos), aunque entregue menos bytes al modelo. El adaptador puede releer el archivo para validar rangos; local_scan_bytes no cuenta todas las lecturas físicas. La reducción es de entrada al revisor, no de todas las operaciones ni de generación. Comparación histórica no simultánea; nuevo render cambia espacios y tokenización. Coste monetario no verificado.

## Hallazgos y límites

1. Recuperar evidencia anotada no es lo mismo que recuperar evidencia útil. El primer documento tiene 0/1 párrafos anotados cubiertos, pero recupera el contraste entrenamiento/evaluación ausente del pasaje anotado. Esa tasa no es un score de fidelidad.
2. El segundo recupera 1/2 párrafos anotados y conserva la lista de idiomas. No se exige duplicación de pasajes para aceptar la lista.
3. La consulta lexical también recupera texto genérico sobre modelos. El código filtra stopwords españolas, no inglesas, y usa coincidencia de términos sin distinguir sus funciones. Es un mecanismo inspeccionado, no causa aislada mediante experimento.
4. Selección parcial más juicio sufficient no demuestra exhaustividad. El caso denoising sigue abierto. No se ejecutó síntesis nueva ni reparación; no es validación end-to-end.

## Decisión y siguiente acción

Mantener sin activar la integración de suficiencia como control decisorio en CLI. Siguiente incremento propuesto: recuperación en dos pasos que haga explícitas las subpreguntas de una consulta plural (qué evaluaciones y qué datos usa cada una), con presupuesto compartido y retorno a fuente; debe mostrar si recupera la evaluación ausente. Preservar el resultado anterior y probar también consultas nuevas, evitando ajustar exclusivamente este caso. No prometer exhaustividad por aumentar top_k.

## Reproducción

`prepare.py` requiere las entradas privadas del corpus y piloto previo, conserva hashes y rechaza un directorio ya existente. `run.py` usa Llavero mediante el transporte previo; no repetir journals existentes. `score.py` verifica hashes, payloads y subcadenas, y calcula métricas sin nuevas llamadas. Inputs/journals ignorados por Git. No hubo cambios de código de producto ni de defaults.
