# Piloto de consultas sobre documentos aportados

Carpeta de trabajo local para la CLI de consulta de Ágora. Independiente del
experimento congelado `../agora-skevi-v1/`; no incorpora sus entradas ni reglas.

## Documento original

- Archivo: `inputs/raw/transcripcion-planeacion-capacidad-servicios-medicos.txt`.
- Procedencia: aportado por el Operador en `experiments/inputs_test/trascripcion.txt`.
- Reubicado el 2026-09-17; la fecha de la reunión no está establecida.
- Texto UTF-8, 19.883 bytes; contenido original sin correcciones.
- SHA-256: `6c02253994aa9526853560eece91697b7130ed9771d479cfdbaa12c3dfa040f8`.

Transcripción sobre infraestructura, capacidad, demanda y proyección de servicios
médicos, con errores de transcripción aparentes y referencias a material no
adjunto. No se considera acta validada ni fuente suficiente para fijar reglas
clínicas o de cálculo. El original completo no se ha enviado a GLM.

`inputs/` queda excluido de Git por el `.gitignore` local. El original completo
se conserva en `raw/`. Una preparación futura debe guardarse aparte, mantener
vínculo con el original e identificar qué se seleccionó o corrigió.
La CLI actual admite hasta 4.096 bytes por fuente; este archivo aún no cabe.
Esta organización no implica una corrida, publicación o admisión a memoria.

## Primer envío autorizado de fragmento

El Operador autorizó el 2026-09-17 enviar a glm-5.3-flash únicamente el fragmento
preparado de auxiliares del diagnóstico (2.233 bytes) y sus preguntas.
Entradas, protocolo y resultados locales: `inputs/runs/auxiliares-diagnostico-v1/`.
La procedencia de preparación conserva el estado histórico previo al envío;
el registro de ejecución documenta el envío posterior. No se autorizó publicar
el documento ni convertir el contenido de la transcripción en reglas validadas.
