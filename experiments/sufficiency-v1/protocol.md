# Suficiencia en observación v1

Siete casos sintéticos nuevos, conocidos por productor; no holdout ni calibración.
Referencia fijada antes de ejecutar en cases.json. PositivosE1/E5/E6; negativos
E2/E3/E4/E7. Sólo preguntas y pasajes seleccionados se envían al modelo, nunca
criterios ni decisionesesperadas ni pasajes excluidos. El proceso local puede
leer original para comprobar identidad; eso no lo convierte en contexto del modelo.

Máximo7solicitudes,una por caso;glm-5.3-flash,temperatura0,2048tokens,socket90s,
deadlineproceso110s. Sin retry ni ajustes después de ver resultados. Código,fuentes,
criterios y protocolo congelados. Credencial del laboratorio sólo en entorno.
Detener tras dos fallos proveedor consecutivos o deadline. Rechazo estructural
es resultado conservado. Ninguna respuesta activa lecturas adicionales ni memoria.

Métrica principal:falsas aprobaciones suficiente en los cuatro negativos. También
falsos rechazos/indecisión en positivos, citas,explicación,uso,latencia. Un fallo
estructural no se transforma en un juicio correcto. Revisar semántica por separado.
Si aparece una falsa aprobación,no promover a automatización. Aunque no aparezca,
sólo hay evidencia exploratoria; se conserva modo observación. No desplegar ni
instalar TypeSafe ni usar datos reales en este ensayo.
