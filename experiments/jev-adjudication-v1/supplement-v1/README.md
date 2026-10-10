# Suplemento ciego: omisiones de Jev en dos documentos QASPER

El paquete contiene las dos respuestas verdaderas pero incompletas que Jev
marcó `unsupported` en `jev-heldout-qasper-v1`, más las respuestas completas
respectivas como controles positivos. Son cuatro fichas y dos fuentes. La
selección es deliberada, retrospectiva y preparada por el productor. No es
una muestra prospectiva ni una adjudicación humana.

`prepare.py` comprueba hashes del dataset y de las fuentes congeladas antes de
crear el paquete. `blind.zip` contiene ocho archivos en `blind/`, sin la llave
`sealed/`, y tiene SHA-256
`11c202901d7382793d26ecfc97370de2ccf058a2483d72c99ff21efdd1cb45ad`.
El archivo ZIP y los logs crudos se conservan sólo localmente; fichas, fuentes,
llave, hojas fijadas y recibos de intento quedan versionados aquí. La copia
exacta de la fuente conserva espacios finales del dataset; `.gitattributes`
excluye únicamente esas líneas del chequeo de espacios de Git.

Se hicieron **dos llamadas nuevas**, una a Codex CLI solicitando `gpt-6-sol` y
una a OpenCode solicitando `zai-coding-plan/glm-5.3-flash`, en ese orden, con
un intento y cero reintentos por programa. Cada directorio de trabajo tenía
únicamente la copia ciega. El [congelado](model-panel-freeze.json) identifica
la solicitud; los [recibos](results/) consignan salida, hashes y tiempo. El
modelo efectivo es `unknown`: la solicitud y los eventos CLI no acreditan por
sí solos la identidad del ejecutor.

Las dos hojas se validaron y fijaron por hash antes de abrir la llave. El
[cotejo](results/comparison.json) observó:

| Variante | Jev previo | Codex | OpenCode |
| --- | --- | --- | --- |
| Datasets, omisión | `unsupported/omitted` | `supported/omitted` | `supported/omitted` |
| Baselines, omisión | `unsupported/omitted` | `supported/omitted` | `supported/omitted` |
| Datasets, completa | `supported/complete` | `supported/complete` | `supported/complete` |
| Baselines, completa | `supported/complete` | `supported/complete` | `supported/complete` |

Las citas fueron cotejadas con las fuentes: `S-9b5fd85c.txt:71` contiene
Europarl v9, NewsTest2013 y NewsTest2014; `S-987604aa.txt:91-99` enumera LDA,
Doc-NADE, HTMM y GMNTM. Las respuestas omitidas afirman sólo elementos de esas
listas. Las completas incluyen los elementos faltantes. El registro visible
de herramientas contiene siete comandos de lectura/búsqueda de Codex y ocho
lecturas/listados de OpenCode, todos bajo `blind/`. No se observó acceso a la
llave en esos eventos; ese registro no garantiza aislamiento del proceso.

La instrucción ciega heredada dice «siete textos» por un error de copia; el
directorio, ZIP, prompt y congelado indican dos fuentes. No se corrigió el
paquete después de la primera entrega para conservar el mismo hash en ambas
llamadas. OpenCode añadió 287 bytes de prosa tras el JSON; la hoja fijada
extrae el objeto inicial sin cambiar su juicio.

**Conclusión limitada:** estos controles refuerzan el diagnóstico de una
confusión de Jev entre respaldo de afirmaciones y cobertura. No demuestran
fiabilidad general de Codex/OpenCode, independencia humana, utilidad para CTIM
ni que una composición automática sea segura. No hubo llamadas nuevas a Jev ni
activación en Ágora.

Reproducción offline del material y la comparación ya fijada:

```sh
.venv/bin/python experiments/jev-adjudication-v1/supplement-v1/prepare.py verify
.venv/bin/python experiments/jev-adjudication-v1/supplement-v1/compare.py
```

El segundo comando verifica el resultado existente contra las hojas fijadas,
la llave y los recibos previos; no vuelve a llamar a proveedores.
