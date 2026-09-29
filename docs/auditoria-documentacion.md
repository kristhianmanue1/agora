# Auditoría documental de Ágora — 2026-09-29

## Alcance y método

Se inventariaron todos los Markdown versionados o nuevos no ignorados del repositorio, incluyendo raíz, `docs/` y `experiments/`. Se recorrió el texto completo mediante comprobaciones mecánicas de enlaces locales, módulos Python referenciados, tamaño e identidad SHA-256; se contrastaron manualmente las afirmaciones de estado operativo y próximos pasos con código, ayuda CLI y resultados de las ejecuciones recientes.

Inventario por archivo y comprobaciones: [documentation-audit.json](documentation-audit.json). Reproducir desde la raíz:

```bash
python3 scripts/audit_docs.py > docs/documentation-audit.json
```

Esta cobertura de archivos no equivale a revalidar semánticamente cada resultado histórico. No se repitieron todas las campañas, no se verificaron enlaces externos ni tarifas vigentes, y no se promovieron decisiones o protocolos por recencia. Los documentos recuperados no otorgan autoridad.

## Hallazgos y acciones

| Hallazgo | Corrección | Límite conservado |
|---|---|---|
| AGENTS presentaba recuperación y CLI como totalmente pendientes | Actualizada descripción del incremento implementado y arquitectura todavía pendiente | No se declara motor completo ni revisión fiable general; bloque AN-KLA intacto |
| README no guiaba a subpreguntas/generación ni distinguía credenciales de Jev | Nuevas rutas y proveedores explícitos | No hay una CLI única para todas las APIs |
| Consolidaciones mezclaban fotografías antiguas con próximos pasos | Aviso temporal y enlace al estado actual | Conteos, resultados y recomendaciones originales no se reescriben |
| Guía de subpreguntas seguía pidiendo conectar el generador | Enlace al consumidor y ensayo ejecutado | Resultado rechazado conservado; revisor no conectado automáticamente |
| Ejemplo de Llavero usaba consumidor relativo | Intérprete y script absolutos en el ejemplo | Ruta de checkout debe adaptarse en otro equipo |
| Era difícil conocer el estado sin reconstruir múltiples informes | `estado-actual.md` e inventario completo | No sustituye decisiones arquitectónicas ni fuentes de evidencia |

Los documentos de decisiones de septiembre y protocolos congelados conservan su texto: “pendiente” dentro de una fotografía histórica no se convierte en estado actual. El estado operativo remite a las guías y evidencia posteriores. Las campañas previas no pasan de fallidas a correctas por mejoras nuevas.

## Comprobaciones

- Enlaces locales Markdown resueltos y módulos Python documentados existentes, según inventario. Que un archivo exista no prueba reproducibilidad desde un clon limpio: algunos datos son locales o externos.
- Ayuda de `agora_issues.py` incluye recuperación y generación desde plan.
- Regresión del código conectado: 458 pruebas aprobadas; cinco pruebas de generación incluyen integridad, fuente cambiada, citas, códigos de salida y rechazo de directorios reutilizados.
- AN-KLA verifica correctamente; se mantiene el aviso de cambios fuera del bloque administrado. No se reinstaló contexto ni se escribió memoria.
- Autorrevisión del productor, sin revisión independiente.

## Lectura recomendada

1. [Estado actual](estado-actual.md): capacidades y límites.
2. [Subpreguntas](subpreguntas.md): recuperación y cobertura.
3. [Generación desde plan](generacion-desde-plan.md): uso, ejecución real y rechazo.
4. [CLI de ampliación](ampliacion-cli.md): revisiones y recuperación, contrato separado.
5. Informes de experimentos y decisiones originales según la pregunta concreta.

Próxima prioridad técnica: referencias por ID en el consumidor nuevo, antes de cambiar tolerancias de citas o repetir llamadas. OCR, estructura automática y validación con casos reservados permanecen pendientes.

## Corrección posterior: descripción L0…Ln

La auditoría inicial no detectó una extrapolación del estado: se había trasladado
la propuesta de niveles de septiembre a los pendientes actuales como si fuera
un requisito vigente de implementación. A petición del Operador se corrigieron
AGENTS, README y estado actual; se añadió una aclaración al documento de origen.
El mapa operativo se expresa por fuentes, evidencia, derivados, afirmaciones,
cuestiones y revisiones. No se afirma sustitución general de contratos históricos
ni se modifica código. Este hallazgo ilustra que inventariar todos los documentos
y verificar sus enlaces no demuestra consistencia semántica completa.
