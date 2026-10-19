# Verificación bilateral Skopos ↔ Ágora v1

**Estado:** ejecutada 2026-10-19, sólo lectura. Ningún repositorio se
modificó. Ejecuta la puerta de verificación bilateral del
[contrato Skopos ↔ Ágora](../docs/contrato-combinacion-skopos-borrador-v1.md)
aceptado por el Operador.

## Qué comprueba

Que los artefactos Skopos consumidos por el [ensayo bilateral de la página
15](../ctim-v02-bilateral-v1/README.md) puedan confirmarse desde los registros
propios de Skopos (repositorio local `~/www/aria/skopos`):

1. copias byte-idénticas de `request.json` y `response.json` en el árbol de
   Skopos;
2. copias con contenido normalizado (JSON ordenado);
3. enlace lógico interno: `request_id` compartido y reproducibilidad local de
   `request_sha256`;
4. referencias de custodia de Skopos al original (hash del PDF);
5. presencia de los bytes del original en algún repositorio.

## Reproducir

```bash
.venv/bin/python experiments/skopos-bilateral-verify-v1/verify.py
```

## Resultado y lectura honesta

**`bilateral_not_confirmed`.** Los hallazgos negativos son el resultado de la
puerta, no defectos del script:

- Skopos **referencia** el original por hash en sus registros de custodia,
  pero sus directorios `custody-delivery/` y `document-delivery/` están vacíos
  y **ninguna copia** del par petición/respuesta servido existe en su árbol
  de corridas.
- La huella `request_sha256` de la respuesta no se reproduce desde los bytes
  que Ágora conserva (crudos ni canónicos): la calculó Skopos sobre su propia
  serialización, así que el enlace hoy no es verificable por el consumidor.
- Los bytes del PDF original no están en ninguno de los dos repositorios;
  la verificación de integridad del intercambio quedaría en `not_checked`.

## Qué exige esto antes de la vigencia del contrato

Está nombrado en `runs/RESULTS.json`. En síntesis: retención duradera de los
pares servidos (o consumo sólo desde corridas duraderas de Skopos), huella
reproducible desde los bytes del consumidor, y acceso al original para la
verificación. El caso reservado sigue pendiente y requiere una derivación
Skopos de una página no consumida por Ágora.
