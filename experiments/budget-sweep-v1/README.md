# Sensibilidad al presupuesto: 8, 12, 20 y 32 KB decimales

Se fijaron presupuestos de 8.000, 12.000, 20.000 y 32.000 bytes UTF-8 antes de medir,
con los mismos cuatro documentos conocidos y cuatro estrategias. No se ajustaron
selectores por los resultados. Es desarrollo, no validación reservada ni estimación
estadística. El límite se aplica a pasajes seleccionados, no al documento completo
ni a todo el prompt. Los recuperadores leen la fuente entera localmente.

## Recuperación offline: casos con todos los párrafos anotados

| Presupuesto | Léxico | Encabezados | Encabezados/listas | Híbrido |
|---:|---:|---:|---:|---:|
| 8.000 | 1/4 | 1/4 | 2/4 | 2/4 |
| 12.000 | 2/4 | 1/4 | 2/4 | 3/4 |
| 20.000 | 2/4 | 1/4 | 2/4 | 4/4 |
| 32.000 | 2/4 | 1/4 | 2/4 | 4/4 |

Los contextos de 20.000 y 32.000 son idénticos en todos estos casos/estrategias.
Subir el techo no obliga a llenarlo: los selectores agotan sus candidatos. La fusión
lee entre 10.983 y 15.116 bytes con techo 20.000. El selector léxico no resuelve sus
dos fallos al aumentar presupuesto: selección y presupuesto son problemas distintos.

## Respuestas reales y tokens

Se fijó por adelantado probar sólo el híbrido en los dos documentos del reto inducido,
a todos los presupuestos. Se ejecutaron seis contextos distintos; 32.000 reutiliza
el resultado del mismo contexto de 20.000, no cuenta como ensayo independiente.
GLM generador/revisor, Jev por afirmación y citas, una llamada por fase, sin reintentos.

| Caso / techo | Bytes reales | Tokens entrada generador | Tokens total* | Resultado |
|---|---:|---:|---:|---|
| Modelos / 8.000 | 7.883 | 2.718 | 7.432 | Válido; 3/3 requisitos; Jev 4/4 supported |
| Modelos / 12.000 | 11.346 | 3.643 | 6.907 | Válido; 3/3 requisitos; Jev 2/2 supported |
| Modelos / 20.000 | 12.216 | 3.855 | 4.920 | Rechazado: invalid_json; sin revisiones |
| Validación / 8.000 | 7.789 | 2.694 | 6.403 | Válido; 3/3 requisitos; Jev 4/4 supported |
| Validación / 12.000 | 11.442 | 3.519 | 6.296 | Válido; 3/3 requisitos; Jev 3/3 supported |
| Validación / 20.000 | 12.101 | 3.688 | 7.267 | Válido; 3/3 requisitos; Jev 3/3 supported |

*Generación y revisiones realmente ejecutadas. El brazo rechazado no tiene coste
comparable de revisiones. Los tokens de entrada incluyen instrucciones y envoltura,
no sólo fuente. Caché, longitud de respuesta y razonamiento varían; menos texto de
entrada no garantiza menos tokens totales. No inferir causalidad del único rechazo
ni atribuirlo con certeza al tamaño del contexto.

16 llamadas, 39.225 tokens reportados, 102,080 s acumulados de ejecuciones medidas
por el cliente (no tiempo total de pared del trabajo). Precio monetario no medido.
Las respuestas válidas de modelos también nombran GPT-2 y XLNet; la rúbrica original
no los exige y sigue sin garantizar completitud. No hubo adjudicación humana ni
repeticiones para estimar variabilidad. Los votos de modelos no certifican verdad.

## Verificación y archivos

Tres tests: reproducción de 64 selecciones y límites, igualdad con resultados previos
a 12.000 y aliases de contextos idénticos. score.py reproduce solicitudes/respuestas
conservadas y vincula revisiones y citas; sin nuevas llamadas. Los fallos se conservan.
Fuentes, prompts y respuestas completas quedan locales en inputs/runs, excluidos de
Git; los reportes incluyen resultados, respuestas y hashes. Reproducción requiere
el dataset y archivos locales previos. Sin cambios de producto/defaults.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/budget-sweep-v1/tests.py
PYTHONDONTWRITEBYTECODE=1 python3 experiments/budget-sweep-v1/score.py
```

## Decisión

12.000 era una condición experimental, no un óptimo demostrado. No elevar el default
a 20.000 por cuatro casos conocidos. Propuesta siguiente: escalamiento explícito y
trazable, conservando rangos ya leídos y probando techos crecientes cuando falte
evidencia; detenerse sin declarar suficiencia cuando ampliar no aporta pasajes.
Congelar esa política y validarla en documentos nuevos, con rúbricas suficientes,
antes de integrarla. El éxito a 8.000 en dos respuestas tampoco justifica bajar el
límite universal.
