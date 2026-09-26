# Consolidación de Ágora — 2026-09-26

Alcance autorizado: consolidar el incremento acumulado y publicarlo con commit
y push. Base de partida: `dd597f3194c302c9d6d6c55f5a73b043fc69d7fd` en main.
No se promueve una fase ni se acredita fidelidad por publicar código.

## Qué se reúne

Recuperación, cobertura, recorrido, selección de ruta, suficiencia, contratos de
citas, revisiones y sus pruebas; protocolos QASPER, AttrScore y controles.
Se conservan los archivos e informes históricos sin reescribir resultados.
La guía README distingue lo implementado de lo validado semánticamente.

## Estado de evidencia

- La batería local de 293 tests pasa antes de esta consolidación. Comprueba
  comportamiento de código con fixtures; no demuestra exactitud general del LLM.
- [Invariancia](revision-invariancia-01.md): el ensayo de ocho casos quedó
  parcial, con dos intentos de transporte fallidos y ninguna respuesta evaluable.
  Un diagnóstico posterior del transporte funcionó; no valida el ensayo.
- [AttrScore](piloto-attrscore-02.md): piloto acotado; los resultados no autorizan
  afirmar superioridad general ni revisión automática fiable.
- Fuentes grandes: hay recorridos y presupuestos explícitos. No hay garantía de
  cobertura semántica completa para cualquier tamaño o documento.

## Siguiente incremento recomendado

Separar respaldo (afirmación + evidencia) de pertinencia (relación con la pregunta).
La revisión actual recibe ambas cuestiones juntas. Implementar una nueva vía
optativa, conservar las anteriores, fijar controles y medir corrección, omisiones,
latencia y coste. No atribuir una mejora al diseño antes de observar resultados.
No requiere esperar a TypeSafe: ese proveedor sigue siendo una opción comparativa.

## Frontera con Skopos y AN-KLA

Skopos debe evolucionar hacia fuentes diversas: reuniones, chats, mensajería,
código y sesiones de agentes. Cada adaptador conserva identidad, versión,
localizador nativo y alcance de lo capturado. Ágora transforma lo recuperado;
AN-KLA conserva selectivamente registros gobernados. Ninguna conexión convierte
un resumen, recuerdo o resultado de búsqueda en evidencia documental verificada.

El siguiente piloto de integración debe probar una fuente y su corrección,
recuperación de la versión vigente, navegación al original y estados de falta de
acceso/completitud. Mantener entrada local independiente y evitar escrituras
cruzadas implícitas. Implementar conectores adicionales requiere sus fixtures y
contratos concretos; no se declara que ya existan por documentar esta dirección.

## Verificación del contenido preparado para publicación

La misma batería de 293 tests pasó en una exportación limpia del índice Git,
sin `.venv`, inputs privados ni resultados ignorados; se utilizó el intérprete
local existente. Esto comprueba que las pruebas publicadas no dependen de esas
entradas. No convierte los experimentos con proveedor en reproducidos.

Autorrevisión adversarial, sin revisor independiente: se revisaron alcance,
archivos incluidos, patrones de credenciales, enlaces de la guía y límites de
las afirmaciones. No se detectaron patrones de claves en los archivos nuevos.
`git diff --check` sólo señala líneas vacías finales en cuatro fixtures de
fallback y un informe histórico. Se conservan para no cambiar sus bytes;
el resto pasa con esa comprobación específica excluida. No se publican cachés.
