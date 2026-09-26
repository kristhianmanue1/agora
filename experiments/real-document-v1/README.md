# Comparación sobre documento real aportado

Ensayo documental local: dos preguntas fijadas antes de ejecutar, lectura completa
frente a recorrido de cuatro unidades de 4096 bytes más consulta de evidencia.
Mismo modelo y pregunta en cada pareja. Datos, documento y resultados privados
bajo `inputs/` y `runs/`, excluidos de Git. No hay validación clínica ni presupuestal.

`glm-01` preserva un rechazo por límite de salida de 2048 tokens. `glm-02` aumenta
sólo ese límite a 8192, conservando preguntas y criterios. Se detuvo tras el rechazo
estructural de Q1; `continuation.json` registra continuación explícita exclusivamente
con Q2, aún no intentada. Q1 no se repitió dentro de glm-02.

Protocolo, código, fuente preparada y referencia congelados antes de llamar.
Máximo doce solicitudes por ensayo; trece en total contando el primer intento
abortado. Sin reintentos automáticos. Timeout socket90 s; límite por etapa110 s,
o400 s para recorrido de cuatro llamadas. Resultado: `docs/ensayo-documento-real.md`.

El archivo original no se modifica. La extracción conserva párrafos y filas de
las tablas en orden; los separadores de celda son `|`, con numeración de tabla
asignada durante extracción. No hay correspondencia de páginas verificada.
