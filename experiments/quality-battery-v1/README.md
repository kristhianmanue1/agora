# Batería de calidad congelada v1

**Estado:** protocolo congelado antes de cualquier llamada a modelos. Esta
batería es offline: cero redes, cero proveedores vivos. Fecha: 2026-10-19.

## Objetivo

Consolidar en un solo paquete reproducible los controles que demuestran si el
recorrido de consulta con evidencia separa correctamente sus ejes, conserva la
procedencia y maneja la incertidumbre remota. No es una certificación de
calidad semántica: los juicios del proveedor son simulados y sólo verifican
estructura, vocabulario de estados y plomería. La calidad semántica se mide en
las fases con modelos (S1/S3/S4, abajo).

## Los ocho escenarios

| # | Escenario | Qué debe comprobarse | Fase |
|---|---|---|---|
| S1 | Fuente completa y respuesta sencilla | Exactitud de afirmaciones y citas | con modelos (puerta T5) |
| S2 | Información obligatoria ausente | La falta se declara; no se inventa el dato | **offline (esta versión)** |
| S3 | Fuente con contradicciones | Los desacuerdos se preservan, no se resuelven arbitrariamente | con modelos (puerta T5) |
| S4 | Respuesta correcta pero incompleta | La revisión detecta los requisitos omitidos | con modelos (puerta T5) |
| S5 | Cita literal que no respalda | La validez de la referencia no se confunde con respaldo semántico | **offline (esta versión)** |
| S6 | Fuente modificada tras fijar su revisión | Se rechaza la ejecución; cero despachos | **offline (esta versión)** |
| S7 | Derivado de fuente incompleta | No se presenta como completo; el hueco no es citable | **offline (esta versión)** |
| S8 | Error/timeout/remoto incierto | Estado correcto, recibo durable, sin reintentos | **offline (esta versión)** |

## Métricas, por eje y sin puntaje global

Cada escenario reporta comprobaciones booleanas separadas por eje: integridad
de referencia, respaldo, suficiencia, cobertura, procedencia y estados de
ejecución. No existe un porcentaje global: un solo fallo se lee con su nombre,
no se promedia.

## Reglas de la fase con modelos (S1/S3/S4)

1. Los casos se congelan (hash de fuentes, preguntas, requisitos y prompts)
   **antes** de la primera llamada; los casos usados quedan de desarrollo y no
   sirven como evaluación reservada posterior.
2. Las etiquetas de referencia se establecen con independencia del modelo
   evaluado; si el productor adjudica, se declara autorevisión.
3. Los umbrales se fijan antes de ver resultados de una versión nueva.
4. Ningún resultado promociona defaults; la aceptación pertenece al Operador.

## Registro de versiones

`freeze.json` registra el hash de cada módulo de `src/agora/*.py` y del
corredor. `verify.py` recomputa el registro y re-ejecuta la batería comparando
resultados con `RESULTS.json`: si el código cambió, falla cerrado y hay que
congelar de nuevo de forma deliberada.

## Reproducir

Desde la raíz del repositorio:

```bash
.venv/bin/python experiments/quality-battery-v1/run.py            # ejecuta y escribe runs/run-001 + RESULTS
.venv/bin/python experiments/quality-battery-v1/run.py --freeze   # regenera freeze.json (deliberado)
.venv/bin/python experiments/quality-battery-v1/verify.py         # integridad + determinismo
```

## Límites

- Proveedores simulados: S2/S5/S8 verifican que el sistema registre y separe
  los estados, no que un modelo real los produzca correctamente.
- S7 usa un original textual de mentira; la relación con un PDF real exige la
  fase con intercambio verificado y no se afirma aquí.
- La batería no mide coste, latencia ni facturación.
