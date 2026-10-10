# Protocolo cerrado para adjudicar respuestas de Ágora

**Enmienda vigente para la ronda solicitada:** el Operador designó a Codex y
OpenCode como revisores por modelo. Ver [MODEL-PANEL.md](MODEL-PANEL.md). La
regla humana siguiente se conserva como requisito para una futura adjudicación
humana y no se atribuye a la ronda de modelos.

## Alcance y procedencia

Este paquete retrospectivo contiene **12 respuestas y siete fuentes**: diez
salidas espontáneas recuperables del T0 emparejado (seis A, cuatro B) y dos
controles preparados. Las B de los casos 03 y 06 no produjeron respuesta
completa en esa serie y permanecen en el conteo estructural original; no se
transforman en abstenciones semánticas ni se incluyen aquí. La B del caso 04
sí tiene texto candidato, aunque su revisión automática quedó incompleta.

El preparador conocía resultados previos de Jev para algunos controles. La
selección fue deliberada. Por ello este paquete es **calibración ciega para el
adjudicador**, no una muestra prospectiva ni adjudicación independiente ya
realizada. Las anotaciones QASPER pueden consultarse después de fijar las
hojas, como referencia adicional, pero no aparecen en `blind/`.

`blind/` contiene únicamente fichas, fuentes, instrucciones y hoja vacía.
`sealed/` vincula cada código con el origen, hash de archivos y controles, y
conserva los criterios de decisión. Para mantener el cegamiento operativo,
entregar **sólo una copia de `blind/`** a cada adjudicador. Una persona con
acceso al repositorio completo puede abrir `sealed/`; la separación de
carpetas no es un control de acceso.

No se realizaron llamadas nuevas a modelos al construir el paquete. No hay
admisión de memoria, activación ni modificación del flujo de Ágora.

## Rúbrica y adjudicación

La [instrucción del lector](blind/INSTRUCTIONS.md) separa claridad de pregunta,
respaldo de cada afirmación y cobertura global. Una respuesta parcial puede
tener respaldo correcto y cobertura `omitted`; las dos etiquetas no se
colapsan. Las abstenciones se cotejan contra la fuente completa. `uncertain`
exige explicación y revisión humana explícita.

Se requieren dos adjudicadores que trabajen sin la llave ni etiquetas de
proveedor. Deben guardar sus hojas y hashes antes de verse mutuamente. Un
tercero resuelve desacuerdos materiales contra la fuente sin ver resultados
de Jev. Si sólo participa uno, el resultado queda provisional. La llave se
abre después de fijar la adjudicación; se conservan desacuerdos y primeras
etiquetas. Las expectativas de los dos controles están en
`sealed/decision-lock.json` y no se transmiten al lector.

## Criterios de decisión fijados ahora

1. Si un control falla su etiqueta esperada, investigar comprensión de la
   rúbrica antes de comparar con Jev; no cambiar en secreto el control ni el
   juicio.
2. Comparar por separado falsos completos y falsos respaldos. Cualquiera de
   ellos impide promover esta configuración como puerta de aceptación.
3. Contar falsas alarmas por separado. Un `uncertain` nunca es pase seguro.
4. Aun con cero falsas aceptaciones en 12 fichas, sólo se habilita considerar
   una prueba prospectiva mayor. Este paquete no autoriza integración ni
   afirma fiabilidad general.
5. Mantener la línea base operativa de revisión explícita hasta demostrar que
   Jev resuelve respuestas adicionales sin nuevas falsas aceptaciones. Una
   matriz de requisitos y citas por respuesta puede servir de comparador
   simple en esa prueba prospectiva; aquí todavía no se ejecuta.

Las reglas exactas y los códigos de los controles están sellados en
`sealed/decision-lock.json`. Para respuestas naturales sin revisión Jev previa,
comparar con el proveedor requeriría llamadas nuevas después de la
adjudicación, con presupuesto y recibos propios. Este protocolo no las hace.

## Comprobación y entrega

```sh
.venv/bin/python experiments/jev-adjudication-v1/build.py verify
```

La verificación reconstruye cada ficha desde el resultado o control de origen,
comprueba los hashes y la hoja vacía. Los archivos de `blind/` pueden copiarse
para el adjudicador; entregar el árbol completo rompería el cegamiento.

`export_blind.py` crea localmente `exports/jev-adjudication-v1-blind.zip` con
sólo esos 21 archivos y un recibo de hashes fuera del ZIP. `exports/` está
ignorado por Git; el archivo no se envía automáticamente a nadie. El destinatario
y el canal deben quedar identificados antes de registrar una entrega.
