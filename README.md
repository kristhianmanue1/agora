# Ágora

Prototipo independiente para transformar y consultar fuentes con referencias
comprobables al original. Produce **candidatos**: una cita literal y un JSON
válido no demuestran por sí solos que una afirmación sea verdadera o completa.

## Qué hay implementado

- Transformación inicial de texto y selección de fragmentos con identidad,
  revisión SHA-256 y localizadores.
- Consulta de varios pasajes, recorrido acotado y selección explícita entre
  fuente completa y evidencia retenida.
- Respuestas por aspectos, afirmaciones con citas literales o identificadores,
  presupuestos y estados que distinguen falta de evidencia y fallo de ejecución.
- Revisión experimental por afirmación y detalle, con adjudicación separada.
- Baterías locales y protocolos QASPER, AttrScore y controles sintéticos.

El adaptador local funciona sin Skopos ni AN-KLA. No hay sincronización de sus
almacenes ni admisión automática de candidatos. Tampoco hay motor completo de
memoria jerárquica ni revisión semántica fiable acreditada.

## Probar sin proveedor

Desde la raíz, con Python 3.10 o posterior y sin dependencias externas para esta
batería:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m agora.evidence_cli --help
```

Los tests usan proveedores simulados; no consumen la API. Las CLI que ejecutan
consultas sí requieren un proveedor explícito y ZAI_API_KEY en el entorno.
No se deben guardar claves en el repositorio. Los límites de bytes de lectura,
tokens de salida y tiempo son distintos; no equivalen a un presupuesto monetario.

## Elegir el recorrido

| Necesidad | Documentación |
|---|---|
| Consultar una fuente por aspectos y citar | [Contrato de evidencia](docs/contrato-afirmaciones-evidencia.md) |
| Fuente completa o recorrido previo | [Selección de ruta](docs/seleccion-ruta-y-partes.md) |
| Fuente que no cabe en una llamada | [Recorrido acotado](docs/recorrido-acotado.md) |
| Revisar el candidato sin aprobarlo automáticamente | [Revisión por afirmación](docs/revision-acotada-por-afirmacion.md) |
| Conocer los límites observados | [Consolidación](docs/consolidacion-2026-09-26.md) |

## Evidencia y reproducción

Los informes de `docs/` describen corridas fechadas, incluidas las fallidas.
Los scripts de `experiments/` conservan protocolos; no todos son ejecutables
desde un clon vacío: algunos requieren datasets externos o resultados de una
corrida anterior. Sus README especifican entradas y presupuesto. Los archivos
privados, entradas de trabajo y resultados crudos ignorados por Git no forman
parte de esta publicación. Un informe no sustituye esos artefactos.

Antes de usar una fuente privada con una CLI externa, decidir expresamente si
puede enviarse al proveedor. El funcionamiento independiente de Ágora no exige
que todas sus ejecuciones sean locales.
