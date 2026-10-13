# Preflight: borrador CTIM RS1, página 21

**Estado:** preflight anterior a la ejecución acotada; resultado posterior en
[`RESULTS.md`](RESULTS.md). El borrador no es una norma aprobada ni vigente.

- Fuente autorizada: `/Users/krisnova/www/aria/skopos/runs/ctim-rs1-draft-local-v1/agora-page21-authorized-582/derived.txt`, **582 bytes**, SHA-256 `ee7ec9b09e6c171dd4e37ed5c1d155366093b2098f38d060a6170f0eefe200c4`.
- Intercambio local: `agora-page21-authorized-582/exchange.json`; PDF original local: `/Users/krisnova/Downloads/2900-003-001_RS1.pdf`, SHA-256 `1f8ad5e506b21cbf6b568b68790d2a757ba870524a6ba341f2dff3637d2494f2`. El PDF se usa para verificación **local** del intercambio; sólo el pasaje UTF-8 se envía al proveedor.
- Pregunta propuesta: «En las actividades 25–27 del pasaje, ¿qué hace CTIM y a quién envía o comunica cada resultado?» Los requisitos y presupuestos están fijados en los JSON de este directorio. No incluyen comentarios de revisión ni otras páginas.
- Modelo solicitado: `glm-5.3-flash` vía perfil `zai` de Llavero. Desactivar para ese proceso la `ZAI_API_KEY` heredada, de forma que Ágora use la credencial `SKOPOS_LLM_API_KEY` inyectada por Llavero. No mostrar ni copiar secretos.
- Presupuesto propuesto: generación 16 384 tokens de salida; respaldo 8192; pertinencia 4096; cobertura 8192; omisiones no solicitadas (`--skip-omissions`). La salida debe ser un directorio **nuevo**. El recorrido podría hacer hasta cuatro llamadas si todas las etapas anteriores terminan; no reintentar automáticamente una llamada incierta.

**Motivo:** el intento con Llavero y 4096 tokens terminó en `finish_reason=length`, contenido vacío y 4093 tokens de razonamiento. Un ensayo anterior con otro pasaje CTIM necesitó 7802 tokens de salida para generar contenido. Elevar el límite es una hipótesis razonable, no garantía de respuesta. El primer HTTP 401 fue un problema de autenticación separado.

**Condición para continuar:** confirmar que este pasaje, pregunta, requisitos, ruta de Llavero y presupuesto siguen siendo el alcance autorizado. Antes de ejecutar, repetir SHA de fuente y original, validar el intercambio, comprobar que el directorio de salida no existe y registrar el hash de la petición lógica. Después, inspeccionar `finish_reason`, contenido, uso reportado, citas, localizadores y faltantes. Una respuesta completa del cliente no constituye aceptación por expertoGobernanza.

**Control offline realizado:** el pasaje y el original coincidieron con los SHA
anteriores; el intercambio verificó 13 segmentos y el original por SHA. Con
la pregunta propuesta, el prompt mide 3285 bytes y la petición lógica de
generación con 16 384 tokens tiene SHA-256
`d901dbb372f40c70e3d781da44e85e4d3d37b5aa208d0d5cdcff556d49aa9f9a`.
Un proveedor sintético produjo un candidato estructuralmente válido y una
cita localizable en los 13 segmentos, con **cero llamadas de red**. Esto no
predice si GLM completará la respuesta. El modo actual de IDs crea una sola
unidad de evidencia de 582 bytes: una cita por afirmación puede abarcar todo
el pasaje, por lo que el consumidor debe revisar la pertinencia de cada
afirmación y no tomar el localizador como respaldo semántico fino.
