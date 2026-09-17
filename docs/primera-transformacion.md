# Primera transformación local de Ágora

Incremento autorizado el 2026-09-16 por el Operador; modelo elegido explícitamente:
glm-5.3-flash. Implementación local sin commit, instalación ni publicación.
Este desarrollo no ejecuta ni modifica el experimento congelado M1-R1. No es
una promoción de M2 ni la evaluación comparativa SKEVI C0/C1.

## Frontera y ubicación

`src/agora/transform.py`: fuente UTF-8 (máximo 4096 bytes), hash esperado por el
llamador, generación candidata y validación de citas. `src/agora/__main__.py`:
CLI explícita con una solicitud HTTPS al endpoint coding de Z.ai, máximo 1200
tokens de salida, timeout45s, sin retry ni redirección. Usa ZAI_API_KEY del entorno;
no instala librerías ni modifica configuración global. tests/ usa unittest.

Esta estructura es la decisión local mínima de este incremento. No define el
motor completo, almacenamiento, catálogo, búsqueda o consolidación. El laboratorio
Microsoft no se importa como biblioteca: el código es stdlib de Ágora. La primera
llamada reutilizó sólo la credencial ya configurada, inyectada sin mostrarla.

## Contrato provisional

Entrada: bytes de fuente saneada, ID, SHA256 esperado y líneas que deben citarse.
Un hash incorrecto o entrada inválida detiene antes de llamar al proveedor.
El hash fija contenido; no prueba verdad, saneamiento ni legitimidad de la fuente.

Salida interna `agora/source-summary-run/v0.1`: fuente exacta, prompt versionado,
modelo solicitado/reportado, uso recibido, salida textual original y candidato.
Cada afirmación debe citar una línea existente con texto exacto. Se rechazan
citas inventadas, cobertura de evidencia requerida incompleta y finish_reason
no igual a stop. Las citas correctas NO prueban que la afirmación se desprenda
de ellas: el estado permanece unreviewed / semantic_support=not_verified.

Los archivos se guardan en un destino nuevo, fuera de la superficie publicada.
No hay transición automática a revisión aprobada, publicación o AN-KLA.
`structural_status=valid` y exit0 significan sólo aceptación estructural.
Salida mal formada queda conservada y rechazada, sin retry automático.
Si falla el proveedor, queda el tipo de error y número de intentos, no su cuerpo
arbitrario. El perfil sólo transporta fuentes sintéticas o ya autorizadas para
ese proveedor; no es un filtro de datos personales ni un sandbox.

## Uso

Desde la raíz, sin instalar:

```bash
PYTHONPATH=src .venv/bin/python -m agora \
  --source /ruta/fuente.txt --sha256 <hash-verificado> \
  --source-id <id> --required-line 1 --model glm-5.3-flash \
  --out /ruta/nueva-corrida
```

Requiere ZAI_API_KEY ya habilitada en entorno; no imprimirla ni incorporarla al
comando como literal. No ejecutar este ejemplo sin fuente y presupuesto concretos.
No existe cifra monetaria verificada; tokens máximos no equivalen a tope de dinero.

## Prueba real de este incremento

Fuente: texto de usuario exacto producido por el parser Skopos sobre la fuente
sintética P1, sin normalización. La ruta anterior de JSONL y offsets queda en
Pinax, enlazada por `agora-source-provenance.json`. No lectura MongoDB ni captura
nueva de conversación privada. Entrada 110 bytes.

Una solicitud real: modelo pedido/reportado glm-5.3-flash, usage 247 prompt +
626 completion = 873 tokens. Reporte del proveedor, no prueba independiente del
modelo subyacente. Se conservó el contenido de respuesta, no reasoning_content.

Resultado: cuatro afirmaciones con citas estructuralmente válidas. Revisión
separada detectó ampliación no respaldada en claim4: «se revisará la fuente».
El original sólo dice «Fecha de revisión pendiente». El candidato original queda
needs_revision en un registro de revisión externo; NO se reescribe result.json.
La corrección editorial separada dice «La fecha de revisión está pendiente» y
no se atribuye a GLM. Esto demuestra un ciclo con revisión, no validación autónoma.

Ruta de evidencia:
`/Users/krisnova/www/aria/pinax/docs/design/2026-09-16-b2-cierre-y-retoma/agora-run-01/`.
La corrida no registró finish_reason y sólo selló inicialmente transform.py.
Se preservaron ambos módulos ejecutados, y se corrigió el código para registrar
los dos hashes y rechazar finalizaciones no confirmadas. La mejora se probó con
transporte simulado; no se gastó una segunda llamada ni se atribuyó el control
retroactivamente a la primera. La finalización del proveedor de ese run es unknown.

## Verificación y límites

14 pruebas nuevas de core/CLI: integridad previa, citas exactas, cita booleana,
reserva de revisión semántica, preservación de salida inválida, stop/length/ausente,
fallo sin retry, redacción de error, hashes de ambos módulos, tamaño y UTF-8.
Freeze M1 verificado sin cambios. No se activaron productor/reviewer de M1.

No se demuestra ahorro de tokens, superioridad sobre L0, robustez general del
resumen, detección automática de alucinaciones, autenticidad de citas, sandbox,
recuperación o consolidación. Para este fixture la cita repite toda la fuente:
la trazabilidad se demuestra, la compresión útil no.

## Revisión final del artefacto

review_agora_slice, instancia separada del productor del código y del resumen,
revisó la corrección editorial de los cuatro claims contra la fuente y la declaró
respaldada para este caso. Verificó que sólo cambió claim4 y que el hash del
original coincide. Reprodujo 14/14 tests sin red. Confirmó los arreglos de
finish_reason y hashes; no reprodujo la llamada GLM ni adjudicó el experimento.
La corrección queda revisada; el original conserva su evaluación needs_revision.
No equivale a aceptación del Operador ni revisión automática de cualquier salida.

El cambio acotado de descripción de estado en AGENTS.md fue autorizado
explícitamente por el Operador después de que la revisión automática exigiera
ese permiso separado. Bloque AN-KLA administrado intacto; no memoria escrita.
