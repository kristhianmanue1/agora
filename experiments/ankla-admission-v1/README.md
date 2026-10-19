# Ensayo de admisión gobernada AN-KLA ↔ Ágora v1

**Estado:** protocolo ejecutado 2026-10-19. Laboratorio desechable: almacén
AN-KLA sintético nuevo en directorio temporal, destruido tras el ensayo. El
almacén `.an-kla` del repositorio no se toca. Cero proveedores vivos: la
ejecución de Ágora usa proveedor simulado.

## Qué prueba este ensayo

Ejecuta las puertas del [contrato de admisión gobernada](../docs/contrato-combinacion-ankla-v1.md):

1. **Referencia real:** una ejecución `answer` completa se produce con
   proveedor simulado, se registra bajo id estable (`r-0001`) y se construye
   la referencia `agora-result-ref/v1` con sus hashes. En este ensayo el
   paquete de consulta no se exporta: `package_sha256` viaja `null` y se
   declara; el ensayo ejercita id, hash de resultado, estado y
   `requires_review`.
2. **Admisión gobernada:** la referencia se admite en el almacén sintético
   sólo por `plan-write` → `commit-write-plan` con autoridad `model_derived`
   (techo summary) y revisión base exacta.
3. **Supersede gobernado:** el fact admitido se sustituye por el flujo del
   propio AN-KLA; el inventario debe mostrar el primero como `sustituida` y
   el segundo vigente.
4. **Control negativo A — autoría falsificada:** una autoridad que declara
   `tool_observed` sin adaptador del host debe fallar cerrado: el plan no
   puede decidir escritura.
5. **Control negativo B — sin ruta de escritura directa:** el código de
   `src/agora` no contiene cliente alguno de AN-KLA; la ausencia es la
   prueba. Se registra el conteo de coincidencias (esperado: cero).
6. **Cierre:** `verify` del almacén sintético con identidad completa.

## Reproducir

```bash
.venv/bin/python experiments/ankla-admission-v1/run.py
```

Requiere el CLI global `an-kla` en PATH. Los pasos, con sus salidas
observadas, quedan en `runs/RESULTS.json`.

## Límites

- La referencia con `package_sha256` null no es la forma objetivo completa
  del contrato; exportar el paquete y admitirlo es el incremento siguiente.
- Un solo caso sintético; no demuestra generalización ni rendimiento.
- No prueba compactación, export/restore ni concurrentes.
- El resultado admitido sigue siendo `requires_review`: nada aquí lo vuelve
  verdad aceptada.
