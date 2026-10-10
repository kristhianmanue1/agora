---
id: preflight-borrador-normativo-ctim-2026-10-10
autor: Codex
fecha: 2026-10-10
proyectos: [agora, skopos, expertoGobernanza]
estado: borrador
derivado_de: []
---

# Preflight para un futuro borrador normativo CTIM

**Estado:** preparación de una prueba, sin fuente recibida ni aceptación
institucional. El Operador describió un documento nuevo como **propuesta en
elaboración**; su contenido, tamaño, custodia, permisos y vigencia son
desconocidos. Este preflight no lo incorpora, no lo envía a un proveedor y no
activa la integración con expertoGobernanza.

1. **Ingreso y clasificación.** Al recibir bytes concretos, registrar ruta,
   tamaño, formato, SHA-256 y versión declarada. Registrar explícitamente
   `estado=borrador` y la procedencia de esa declaración; no convertirla en
   norma aprobada o vigente. Skopos conserva original y derivación si participa.
2. **Selección de evidencia.** Para PDF/HTML, fijar original y manifiesto,
   extraer pasajes pertinentes con localizadores verificables y cotejar
   visualmente tablas, columnas y relaciones actor–actividad. Documentar
   páginas inspeccionadas y huecos. Una fuente de `answer-v2` es un UTF-8 de
   hasta 160 000 bytes; seleccionar pasajes no equivale a cubrir el documento
   completo. No insertar `[omitted]` dentro de una cita que deba exportarse
   con procedencia PDF.
3. **Autorización del proveedor.** Antes de `answer-v2` o `jev-review`, obtener
   la decisión del Operador sobre qué bytes del borrador pueden salir a qué
   proveedor. Registrar modelo solicitado, presupuesto y salida nueva. La
   disponibilidad de credenciales no demuestra autorización de envío.
4. **Consulta acotada.** Fijar pregunta y requisitos, hash de la fuente
   seleccionada y presupuesto por etapa. Ejecutar sólo la entrada optativa
   autorizada; conservar intentos, recibos y faltantes. Si el candidato es
   parcial y la cobertura dice `complete`, marcar el conflicto y mantener
   `requires_review`.
5. **Exportación y contraste.** `export-answer` debe verificar fuente,
   recorrido y, si se pretende citar el original, intercambio y PDF/HTML.
   Cada afirmación debe tener cita literal y rangos/localizadores de todos
   los segmentos usados, sin huecos. expertoGobernanza contrasta las citas
   con el borrador, su pregunta y su gate; la revisión humana decide utilidad
   y cualquier aceptación institucional por separado.

**Mínimo para la primera prueba real:** documento y versión identificables,
clasificación de borrador, SHA del original, pasajes y localizadores cotejados,
pregunta/requisitos, autorización de envío al proveedor elegido y criterio de
revisión del consumidor. Si el documento exige varias fuentes o supera el
límite de una fuente, diseñar selección y composición explícitas antes de
afirmar cobertura global. Jev es una segunda señal optativa, no parte implícita
de las cinco llamadas GLM de `answer-v2`.
