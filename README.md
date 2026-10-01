# Ágora

Prototipo independiente para transformar y consultar fuentes con referencias
comprobables al original. Produce **candidatos**: una cita literal y un JSON
válido no demuestran por sí solos que una afirmación sea verdadera o completa.

**Estado operativo:** [capacidades, límites y próxima prioridad](docs/estado-actual.md).
**Documentación completa:** [inventario y auditoría](docs/auditoria-documentacion.md).

## Qué hay implementado

- Transformación inicial de texto y selección de fragmentos con identidad,
  revisión SHA-256 y localizadores.
- Consulta de varios pasajes, recorrido acotado y selección explícita entre
  fuente completa y evidencia retenida.
- Respuestas por aspectos, afirmaciones con citas literales o identificadores,
  presupuestos y estados que distinguen falta de evidencia y fallo de ejecución.
- Revisión experimental por afirmación y detalle, con adjudicación separada.
- CLI de pendientes: preparación, evaluación, inspección, recuperación y reparación
  explícita separada. [Recorrido reproducible](docs/pendientes-cli.md).
- Baterías locales y protocolos QASPER, AttrScore y controles sintéticos.

El adaptador local funciona sin Skopos ni AN-KLA. No hay sincronización de sus
almacenes ni admisión automática de candidatos. Tampoco hay motor completo de
transformación y consolidación de memoria ni revisión semántica fiable acreditada.

## Probar sin proveedor

Desde la raíz, con Python 3.10 o posterior y sin dependencias externas para esta
batería:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m agora.evidence_cli --help
```

Los tests usan proveedores simulados; no consumen la API. Las CLI que ejecutan
consultas sí requieren proveedor explícito. GLM usa `ZAI_API_KEY`; algunos
comandos también aceptan `SKOPOS_LLM_API_KEY`. Jev utiliza `TYPESAFE_API_KEY`
y sólo participa en los recorridos que lo admiten expresamente.
No se deben guardar claves en el repositorio. Los límites de bytes de lectura,
tokens de salida y tiempo son distintos; no equivalen a un presupuesto monetario.

## Elegir el recorrido

| Necesidad | Documentación |
|---|---|
| Consultar una fuente por aspectos y citar | [Contrato de evidencia](docs/contrato-afirmaciones-evidencia.md) |
| Fuente completa o recorrido previo | [Selección de ruta](docs/seleccion-ruta-y-partes.md) |
| Fuente que no cabe en una llamada | [Recorrido acotado](docs/recorrido-acotado.md) |
| Separar respaldo y pertinencia (optativo) | [Revisión separada](docs/revision-separada.md) |
| Revisar el candidato sin aprobarlo automáticamente | [Revisión por afirmación](docs/revision-acotada-por-afirmacion.md) |
| Batería ampliada y piloto Skopos → Ágora | [Resultados del recorrido](docs/piloto-conjunto-ids-02.md) |
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

Comparación experimental de revisores: [GLM y Jev, 2026-09-28](docs/comparacion-revisores-glm-jev-2026-09-28.md).

Continuación con fuentes externas: [AttrScore reservado y documentos grandes](docs/comparacion-revisores-reservados-2026-09-28.md).

Ampliación controlada: [pasaje pertinente frente a más texto](docs/ampliacion-evidencia-revisores-2026-09-28.md).

Recuperación verificada: [ampliación sin localizador prefijado](docs/recuperacion-ampliacion-revisores-2026-09-28.md).

CLI de ampliación: [preparar, inspeccionar y volver a evaluar](docs/ampliacion-cli.md).

Recuperación local: [subpreguntas y funciones](docs/subpreguntas.md).

Generación conectada: [plan verificado → candidato](docs/generacion-desde-plan.md).

Revisión optativa de suficiencia: [review-coverage](docs/revision-suficiencia-cli.md), con replay o una llamada GLM explícita; sin admisión automática.
Diagnóstico optativo posterior: [diagnose-omissions](docs/diagnostico-omisiones-cli.md), propuestas con localizadores de evidencia y validación semántica todavía parcial.

Recuperación ante omisiones: [propuesta acotada desde una revisión](docs/recuperacion-cobertura.md).
