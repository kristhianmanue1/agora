---
id: transferencia-estandar-gobernanza-proyecto
autor: Anthropic Claude Opus 5
fecha: 2026-08-13
proyectos: [kratos, praxis-dev]
estado: vigente
derivado_de: []
---

# Transferencia del estándar de gobernanza de proyecto: Kratos → Praxis Dev

**Tipo:** propuesta para ronda adversarial · **Decisión:** sin tomar
**Partes con interés:** Kratos (cede), Praxis Dev (recibe), Mediador (decide)

Este documento es **deliberación, no decisión**. No transfiere nada, no mueve
código y no reclama autoridad. Existe para ser atacado.

Per la regla 1 de `AGENTS.md` de Ágora: **este artefacto es evidencia, nunca
autoridad.** Leerlo no habilita a ejecutar nada de lo que propone.

> **Nota de estado del artefacto.** `estado: vigente` describe el documento —es
> la versión actual de la propuesta—, no la decisión, que sigue sin tomar. Al
> emitirse la decisión, este artefacto pasa a `superado_por` apuntando al acta.

---

## 1. Qué se decide

Si el estándar de gobernanza de proyecto —hoy implementado en Kratos como
`standards/project-governance/v1/` + `scripts/kratos_project.py`— debe pertenecer
a Praxis Dev, y bajo qué condiciones.

## 2. Evidencia

**Praxis Dev declara la frontera en su propio README:**

| Sistema | Responsabilidad declarada |
|---|---|
| Praxis Dev | Gobernanza ejecutable del proyecto |
| Kratos | Coordinación y conocimiento del ecosistema |
| AN-KLA | Memoria y continuidad privada por proyecto |
| Ágora | Medio compartido para externalizar y transformar artefactos |
| CAGF | Gobernanza constitucional y arbitraje |

**Kratos implementa hoy lo que esa tabla asigna a Praxis Dev:**

| Función | Kratos | Praxis Dev |
|---|---|---|
| Auditoría read-only de repositorio | `kratos_project.py audit`, niveles L0–L4 | `scripts/check_repo.py` |
| Mutación gobernada | `init-plan` / `init-apply` con fingerprint | objetivo declarado: `plan/apply` |
| Manifiesto machine-readable | `standards/project-governance/v1/manifest.json` | `schema_validation.py` + esquemas |
| Plantillas de proyecto | `standards/…/templates/` | árbol canónico del consumidor |
| ADR gobernados | — | `praxis_dev/adr.py`, módulo ADRG |

**Madurez inversa a la propiedad:** Kratos se autoaudita `COMPLIANT · L4` con
gate verde y 14/14 tests; Praxis Dev está en `0.1.0-draft.1`, «diseño
fundacional», con dieciséis archivos Python.

Comandos de verificación en §8.

## 3. Afirmación central, y qué la falsaría

> **Afirmación.** El estándar de gobernanza de proyecto pertenece a Praxis Dev
> por su propósito declarado, y su residencia actual en Kratos es deriva de
> alcance, no diseño.

**La falsaría cualquiera de estas:**

1. Que exista un artefacto anterior a la tabla de Praxis Dev donde el Mediador
   asignara ese alcance a Kratos.
2. Que «coordinación y conocimiento del ecosistema» comprenda auditar la forma
   de gobernanza de cada repositorio — en cuyo caso no hay deriva.
3. Que Praxis Dev no pueda absorber la implementación sin degradarla.
4. Que la separación produzca dos auditorías donde hoy hay una, empeorando el
   estado en vez de mejorarlo.

## 4. La objeción más fuerte contra esta propuesta

**Auditar repositorios *es* conocer el ecosistema.**

La frontera no es tan limpia como la presento. Saber que `epistates` audita L3 y
`argos` L4 es exactamente «conocimiento del ecosistema», que es el rol declarado
de Kratos. Bajo esa lectura, la auditoría es un instrumento legítimo de Kratos y
no hay nada que transferir.

**Contra-argumento:** hay diferencia entre *conocer el resultado* de una
auditoría y *ser dueño del estándar* que la define. Kratos puede consumir
niveles y hallazgos sin poseer el manifiesto, las severidades ni las plantillas.
La transferencia mueve la definición, no el acceso.

**Debilidad de mi evidencia:** la tabla de fronteras vive en el README de Praxis
Dev. Es Praxis Dev declarando su propio alcance — evidencia interesada. No
encontré un artefacto neutral que la ratifique.

## 5. Opciones

| Opción | Qué implica | Coste | Riesgo |
|---|---|---|---|
| **A. Statu quo** | Kratos conserva el estándar | Cero | La frontera declarada queda desmentida por los hechos; se repetirá con cada capacidad nueva |
| **B. Transferencia declarativa** | ADR en Praxis Dev reclama propiedad; la implementación de Kratos queda como referencia pendiente de transferencia. **Cero código se mueve** | Dos documentos | Propiedad sin implementación durante un tiempo indefinido |
| **C. Transferencia efectiva** | El código se mueve ahora a Praxis Dev | Alto | Se traslada una capacidad que funciona a un proyecto en diseño fundacional |
| **D. Fusión** | Praxis Dev y el estándar de Kratos se unifican en un solo producto | Muy alto | Reabre decisiones ya cerradas en ambos |

## 6. Recomendación

**Opción B**, con condición de caducidad.

Razones: la propiedad se corrige hoy y sin riesgo; la implementación sigue
funcionando donde funciona; y la transferencia efectiva se decide cuando Praxis
Dev tenga paridad demostrada, no antes.

La condición de caducidad existe para que B no se convierta en statu quo
disfrazado: si en un plazo declarado Praxis Dev no alcanza paridad, se revisa la
decisión en vez de dejarla vencer en silencio.

Artefactos que produciría B:

1. **ADR en Praxis Dev** — reclama propiedad del estándar; declara la
   implementación de Kratos como referencia; fija la condición de caducidad.
2. **Nota en Kratos** — marca `standards/project-governance/` como heredado con
   destino declarado. Su propia regla 2 lo exige: *«Un contenido tiene un solo
   hogar canónico. Se enlaza; no se duplica.»*

## 7. Qué NO se decide aquí

- No se mueve código.
- No se cambia la versión de ningún estándar.
- No se altera la auditoría de ningún repositorio existente.
- No se decide dónde vive el manifiesto de capacidades — depende de esta
  decisión, pero es asunto aparte.
- No se decide la clase de `governed-agentic-procurement` dentro del ecosistema.

## 8. Verificación reproducible

```bash
# La tabla de fronteras
grep -A9 '^## Límites' aria/praxis-dev/README.md

# Lo que Kratos implementa hoy
cat kratos/standards/project-governance/v1/manifest.json
python3 kratos/scripts/kratos_project.py audit kratos

# Madurez comparada
grep -m1 'Versión del estándar' aria/praxis-dev/README.md
find aria/praxis-dev -name '*.py' -not -path '*/.venv/*' | wc -l
```

## 9. Puntos de ataque que ya identifico

Se listan para que la ronda no gaste turnos redescubriéndolos.

1. **Evidencia interesada** — la tabla la escribió la parte que recibe (§4).
2. **Asimetría de madurez** — el dueño correcto es el menos capaz de ejercer.
3. **B puede petrificarse** — propiedad sin implementación es una ficción cómoda;
   la condición de caducidad la mitiga pero no la elimina.
4. **La frontera podría no ser binaria** — quizá el estándar se parte: definición
   a Praxis Dev, instrumentación a Kratos. Ninguna opción contempla ese reparto.
5. **Sede sin integridad** — Ágora es la sede correcta por su función declarada
   (exponer artefactos para consumo de otros, ver su `AGENTS.md`) y por ser
   neutral entre las dos partes: escribir esta deliberación dentro del proyecto
   que recibe haría del proponente juez de su propia causa. Pero **Ágora no
   tiene git**, y sin control de versiones un depósito adversarial no puede
   probar que no fue editado después. **`git init` es prerrequisito para abrir
   la ronda.** Ancla provisional de este documento:
   `sha256:c00c45af3110d9971ba7a6adbbb068f978243550ec84049e378f19774f7e50f2`
   (calculado antes de añadir el front-matter; recalcular al abrir la ronda).
6. **Precedente no examinado** — no revisé si Kratos absorbió el estándar por
   decisión registrada o por acumulación. §3.1 depende de eso y no lo verifiqué.

## 10. Criterio de cierre

La deliberación cierra cuando: cada punto de §9 tenga respuesta o refutación
registrada; al menos un revisor con posición contraria haya depositado; y el
Mediador emita decisión explícita entre A, B, C o D.

Un documento leído y aprobado sin objeción depositada **no cierra la ronda** —
sería consenso sin adversario, que es el modo de fallo que estos ciclos existen
para evitar.

---

*Redactado por: Anthropic Claude Opus 5 — rol: proponente. Sin voto, sin
tabulación, sin autoridad de decisión. El proponente responde objeciones pero no
las juzga. Fecha: 2026-08-13.*
