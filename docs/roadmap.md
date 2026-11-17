# qskill — Plan de ejecución por etapas

> Suite de skills de agente para programar proyectos cuánticos multi-framework.
> Repo: `C:\Users\palob\Program\qskill` · OpenSpec inicializado · 0 changes · 0 specs
> Fecha base: 2026-11-17
> Estado: **propuesta, pendiente de aprobación de supuestos (§1)**

---

## 0. Resumen

Construir `qskill` como una **suite de skills por etapa** con un eje híbrido:

- **Skills de etapa** (framework-agnósticas): estrategia, teoría, validación, hardware, mitigación, portabilidad.
- **Skills de framework**: API idiomática y ciclo completo en un SDK.
- **Hub** que decide qué cargar en cada tarea.

Se ejecuta en 6 etapas con corte vertical temprano: la Etapa 1 prueba formato, harness y tono con 3 skills antes de escalar a 10.

```
Etapa 0        Etapa 1         Etapa 2        Etapa 3        Etapa 4        Etapa 5
Fundacion  ->  Corte vertical  Algoritmos  -> Multi-SDK   -> Hardware   -> Consolidacion
harness        3 skills        + framing      5 skills      8 skills       release
~2 dias        ~4 dias         ~3 dias        ~4 dias        ~4 dias        ~2 dias
```

**Total estimado:** 19–21 días de trabajo efectivo (unas 3 semanas a tiempo parcial).

---

## 1. Supuestos (confirmar antes de Etapa 1)

| # | Decisión | Default propuesto |
|---|---|---|
| A1 | División de skills | Híbrido: hub + 3 framework + 6 etapa |
| A2 | Alcance Etapa 1 | `quantum-project` + `qiskit-workflow` + `quantum-validation` |
| A3 | Idioma del contenido | Inglés en `SKILL.md` y referencias; español en conversación |
| A4 | Harness de evals | Propio y mínimo (Python stdlib-ish), sin `promptfoo` |
| A5 | Hardware en v1 | Solo IBM Quantum vía Qiskit; Braket/Google en v2 |
| A6 | Gestor de entorno | `uv` + Python 3.12 + venv por proyecto |
| A7 | Formato de reglas | 1 change de OpenSpec por etapa |

Si alguna cambia, se ajusta la etapa correspondiente; ninguna bloquea la Etapa 0.

---

## 2. Etapa 0 — Fundación

**Objetivo:** que escribir un skill nuevo sea mecánico y verificable.

### Entregables

```
qskill/
├── .python-version                 # 3.12
├── pyproject.toml                  # proyecto uv, extras por framework
├── uv.lock
├── .gitignore
├── README.md                       # qué es, instalación, cómo validar
├── docs/
│   ├── conventions.md              # anatomía, reglas de description, versionado
│   ├── roadmap.md                  # copia de este plan
│   └── skill-template/
│       ├── SKILL.md
│       ├── references/api-map.md
│       └── scripts/check_env.py
├── scripts/
│   ├── new_skill.py                # scaffolder desde la plantilla
│   ├── skill_lint.py               # frontmatter, longitud, triggers, referencias
│   └── run_snippets.py             # ejecuta bloques ```python de un SKILL.md
└── evals/
    ├── schema.md                   # formato de caso de eval
    ├── run.py                      # runner
    └── cases/                      # vacío al cierre de esta etapa
```

### Tareas

1. Crear `pyproject.toml` con extras: `qiskit`, `pennylane`, `cirq`, `dev`. Pinnear versiones resueltas al momento (`uv add --extra qiskit qiskit qiskit-aer`).
2. `.python-version` = 3.12; documentar `uv sync --all-extras` en README.
3. Escribir `docs/conventions.md` con:
   - anatomía de directorios (§3),
   - límite de 500 líneas para `SKILL.md`,
   - regla de `description` exclusiva y longitud 60–500 caracteres,
   - regla "framework = sintaxis, etapa = estrategia",
   - política de snippets ejecutables.
4. `scripts/new_skill.py <name>`: copia la plantilla, sustituye placeholders, valida que el nombre no exista.
5. `scripts/skill_lint.py` con estas reglas:
   - `name` del frontmatter == nombre del directorio,
   - `description` presente, longitud válida, sin duplicados exactos,
   - `SKILL.md` ≤ 500 líneas,
   - todo enlace local en `references/` existe,
   - sin `TODO`, `FIXME`, `XXX`,
   - aviso si el `description` comparte ≥ 4 keywords con otro skill (colisión de trigger).
6. `scripts/run_snippets.py`:
   - extrae bloques ` ```python `,
   - ejecuta cada bloque en subproceso aislado con timeout de 120 s,
   - soporta marcador `# qskill: skip` para bloques que requieren credenciales,
   - resumen por archivo, exit code 1 si algo falla.
7. `evals/schema.md` + `evals/run.py` (runner genérico; sin casos aún).
8. Actualizar `README.md` con la sección "Cómo añadir un skill" y "Cómo validar".

### Esquema de caso de eval (definido aquí, usado desde Etapa 1)

```yaml
id: bell-state
skill: qiskit-workflow
prompt: |
  Crea un Bell state en Qiskit y mide 1024 shots.
checks:
  - kind: required_patterns
    patterns: ["QuantumCircuit", "SamplerV2|StatevectorSampler"]
  - kind: forbidden_patterns
    patterns: ["execute\\(", "BasicAer"]
  - kind: snippet_runs          # extrae el código de la respuesta y lo ejecuta
  - kind: numeric_close         # opcional: valor esperado + tolerancia
    target: 0.5
    tolerance: 0.05
```

### Criterio de aceptación

- `uv run python scripts/skill_lint.py .agents/skills` pasa sobre las 6 skills de OpenSpec (solo lint).
- `uv run python scripts/new_skill.py demo` genera un skill y `lint` lo acepta; luego se borra.
- `run_snippets.py` detecta una fallo deliberado en un fixture.
- `evals/run.py --list` funciona con 0 casos.

### Change OpenSpec

`skill-foundation` → capability `skill-authoring`.

---

## 3. Etapa 1 — Corte vertical

**Objetivo:** probar que el formato funciona con 3 skills reales y evals que corren.

### Entregables

```
.agents/skills/
├── quantum-project/
│   ├── SKILL.md                    # hub: ciclo de vida, decision tree, routing
│   ├── references/
│   │   ├── lifecycle.md            # diagrama por etapa
│   │   ├── framework-choice.md     # matriz Qiskit/Cirq/PennyLane
│   │   └── project-layout.md       # estructura de proyecto recomendada
│   └── scripts/check_env.py
├── qiskit-workflow/
│   ├── SKILL.md
│   ├── references/
│   │   ├── api-map.md              # Qiskit 2.x: imports, primitives, circuitos
│   │   ├── patterns.md             # Bell, GHZ, QFT, medición, parámetros
│   │   └── migration-1x-2x.md      # qué desapareció y por qué
│   └── scripts/check_env.py
└── quantum-validation/
    ├── SKILL.md
    ├── references/
    │   ├── simulation-modes.md     # statevector / shots / density matrix
    │   ├── testing.md              # seeds, tolerancias, snapshot
    │   └── statistics.md           # error estándar, intervalos, shots
    └── scripts/check_env.py
```

```
evals/cases/
├── routing/
│   ├── qiskit-task.yaml            # debe cargar qiskit-workflow
│   ├── validation-task.yaml        # debe cargar quantum-validation
│   └── ambiguous-task.yaml         # debe cargar el hub primero
├── qiskit-workflow/
│   ├── bell-state.yaml
│   ├── transpile-line.yaml
│   ├── sampler-v2.yaml
│   └── reject-old-api.yaml
└── quantum-validation/
    ├── bell-distribution.yaml      # 50/50 ± tolerancia
    ├── ghz-state.yaml
    └── seed-reproducibility.yaml
```

### Tareas

1. Redactar `quantum-project/SKILL.md`: cuándo cargar, árbol de decisión, tabla de delegación a cada skill, layout de proyecto, política de versiones.
2. Redactar `qiskit-workflow`: flujo construir → transpilar → ejecutar → medir; `SamplerV2`/`EstimatorV2`; `qiskit-aer`; errores típicos de 2.x.
3. Redactar `quantum-validation`: cómo se comprueba un circuito, modos de simulación, tests deterministas, cuándo usar shots vs statevector, reporte de incertidumbre.
4. Escribir 3 `check_env.py` (versión mínima, imports críticos, mensaje de fix).
5. Crear los 10 casos de eval y hacerlos correr con `evals/run.py`.
6. Ejecutar `run_snippets.py` sobre los 3 skills en venv limpio.
7. Ajustar `description` hasta que los 3 evals de routing acierten.

### Criterio de aceptación

- ≥ 80 % de evals en verde (8/10).
- 100 % de snippets ejecutan en venv limpio.
- Lint sin warnings.
- Un humano lee los 3 `SKILL.md` y puede seguir el flujo sin preguntar.

### Riesgo específico

Si los triggers siguen colisionando, se separa `quantum-validation` en "validación de circuitos" y "estadística de resultados". No se toca antes de medir.

### Change OpenSpec

`core-quantum-skills` → capabilities `skill-routing`, `framework-qiskit`, `circuit-validation`.

---

## 4. Etapa 2 — Algoritmos y framing

**Objetivo:** cubrir el "qué" del proyecto, no solo el "cómo".

### Entregables

```
.agents/skills/
├── quantum-algorithms/
│   ├── SKILL.md                    # catálogo + criterio de elección
│   └── references/
│       ├── variational.md          # VQE, QAOA: ansatz, optimizador, barren plateaus
│       ├── search.md               # Grover, amplitude amplification
│       ├── phase-estimation.md     # QPE, QFT, applications
│       ├── simulation.md           # Hamiltonian simulation (Trotter, LCU)
│       └── encodings.md            # Jordan-Wigner, Bravyi-Kitaev, Pauli strings
└── quantum-problem-framing/
    ├── SKILL.md                    # go/no-go, baseline clásico, recursos
    └── references/
        ├── readiness-checklist.md
        ├── resource-estimation.md  # qubits, profundidad, shots, tiempo
        └── classical-baseline.md   # cómo justificar quantum vs clásico
```

```
evals/cases/quantum-algorithms/
├── vqe-h2.yaml                     # energía cerca de -1.137 Ha ± 0.05
├── grover-3-qubit.yaml             # marca encontrada con prob. > 0.9
├── qft-inverse.yaml                # QFT + QFT^-1 == identidad
└── encoding-jw.yaml                # Hamiltoniano 4-qubit correcto
```

### Tareas

1. Escribir `quantum-algorithms/SKILL.md` como catálogo con árbol de elección (problema → algoritmo) y criterios de éxito numéricos.
2. Referencias por familia con pseudocódigo **y** un snippet ejecutable de referencia (Qiskit, porque es el framework ya cubierto).
3. `quantum-problem-framing` con checklist de readiness y tabla de estimación de recursos.
4. Evals centrados en corrección numérica, no en sintaxis.
5. Verificar que los snippets de algoritmos siguen ejecutando (regresión de Etapa 1).

### Criterio de aceptación

- 4/4 evals de algoritmos en verde.
- Cada referencia de algoritmo tiene al menos 1 snippet ejecutable.
- El hub enlaza a estos skills y los evals de routing siguen verdes.

### Change OpenSpec

`algorithm-skills` → capabilities `quantum-algorithms`, `problem-framing`.

---

## 5. Etapa 3 — Multi-framework

**Objetivo:** segundo y tercer SDK, y la primera prueba real de portabilidad.

### Entregables

```
.agents/skills/
├── pennylane-workflow/
│   ├── SKILL.md
│   ├── references/
│   │   ├── api-map.md              # QNode, devices, gradients, shots
│   │   ├── patterns.md
│   │   └── autodiff.md             # torch/jax/autograd
│   └── scripts/check_env.py
└── cirq-workflow/
    ├── SKILL.md
    ├── references/
    │   ├── api-map.md              # Circuit, Moment, Simulator, optimizers
    │   ├── patterns.md
    │   └── cirq-google.md          # solo si aplica en v2
    └── scripts/check_env.py
```

```
evals/cases/
├── pennylane-workflow/
│   ├── bell-state.yaml
│   ├── vqe-gradient.yaml           # gradiente finito y descendente
│   └── device-shots.yaml
├── cirq-workflow/
│   ├── bell-state.yaml
│   ├── moments-optimize.yaml
│   └── simulator-sampling.yaml
└── cross-framework/
    ├── equivalent-bell.yaml        # 3 SDKs -> misma distribución
    └── equivalent-ghz.yaml
```

### Tareas

1. `pennylane-workflow`: QNode, devices por defecto, gradientes, shots, integración con `quantum-validation`.
2. `cirq-workflow`: `Circuit`/`Moment`, `Simulator`, `optimizers`, sampler propio.
3. `check_env.py` para ambos.
4. Evals de equivalencia cross-framework: mismo circuito, misma distribución dentro de tolerancia.
5. Actualizar `quantum-project/references/framework-choice.md` con la matriz ya validada empíricamente.
6. Revisar `quantum-algorithms`: los snippets de referencia siguen en Qiskit; añadir nota de traducción a los otros SDKs.

### Criterio de aceptación

- 8/8 evals nuevos en verde.
- Distribuciones equivalentes (Bell, GHZ) dentro de tolerancia en los 3 frameworks.
- Lint sin colisiones de trigger entre los 3 skills de framework.

### Change OpenSpec

`multiframework-skills` → capabilities `framework-pennylane`, `framework-cirq`, `cross-framework-equivalence`.

---

## 6. Etapa 4 — Ciclo de vida en hardware

**Objetivo:** llevar un circuito de la simulación a un backend real sin romper nada.

### Entregables

```
.agents/skills/
├── quantum-hardware-execution/
│   ├── SKILL.md                    # seleccionar backend, enviar, gestionar jobs
│   └── references/
│       ├── providers.md            # IBM (v1); Braket/Google (v2)
│       ├── backend-selection.md    # qubits, error rates, cola, costo
│       ├── transpile-for-hardware.md
│       └── job-management.md       # estados, reintentos, cancelación
├── quantum-error-mitigation/
│   ├── SKILL.md
│   └── references/
│       ├── noise-characterization.md
│       ├── mitigation-techniques.md # ZNE, PEC, twirling, readout, DD
│       └── reporting.md             # cómo reportar incertidumbre
└── quantum-portability/
    ├── SKILL.md
    └── references/
        ├── qasm3.md                 # export/import, limitaciones
        ├── translation-matrix.md    # Qiskit <-> Cirq <-> PennyLane
        └── equivalence-checks.md
```

```
evals/cases/hardware/
├── dry-run-provider.yaml           # mock de provider, sin red
├── backend-filter.yaml             # elige backend por criterios
├── transpile-native.yaml           # solo gates nativos
├── zne-apply.yaml
├── readout-mitigation.yaml
└── qasm-roundtrip.yaml
```

### Tareas

1. `quantum-hardware-execution` con degradación explícita: si no hay credenciales → simulador, y decirlo.
2. `quantum-error-mitigation` con criterio de cuándo mitigar y cuándo no (overhead).
3. `quantum-portability` con OpenQASM 3 como lingua franca y matriz de traducción.
4. **Mocks**: `evals/support/mock_provider.py` para que los evals nunca toquen red ni gasten jobs.
5. Evals de dry-run, selección de backend, roundtrip QASM.
6. Documentar en el hub el flujo completo simulación → hardware → mitigación → reporte.

### Criterio de aceptación

- 6/6 evals en verde **sin red**.
- Ningún snippet requiere credenciales para pasar (los que las requieren llevan `# qskill: skip`).
- Ejecución real de un Bell state en IBM verificada manualmente una vez (no automatizada).

### Change OpenSpec

`hardware-lifecycle-skills` → capabilities `hardware-execution`, `error-mitigation`, `portability`.

---

## 7. Etapa 5 — Consolidación y release

**Objetivo:** que el repo sea usable por alguien más (o por ti en 6 meses).

### Entregables

- `README.md` final: qué es, instalación con `uv`, lista de skills con triggers, cómo validar.
- `docs/install.md` multiplataforma (Windows/macOS/Linux).
- `scripts/ci.py` que corre lint + snippets + evals de una vez.
- `docs/version-matrix.md`: qué versión de cada SDK soporta la suite.
- Revisión de todas las `description` como conjunto (colisiones globales).
- Tag `v0.1.0`.
- Archivar los 5 changes de OpenSpec en `openspec/changes/archive/`.

### Criterio de aceptación

- `uv run python scripts/ci.py` verde de punta a punta en un clon limpio.
- Un usuario nuevo instala y ejecuta el eval del Bell state siguiendo solo el README.
- `openspec list` sin changes activos; `openspec/specs/` con 8+ capabilities.

---

## 8. Estructura final del repo

```
qskill/
├── .agents/skills/
│   ├── quantum-project/            # hub
│   ├── qiskit-workflow/
│   ├── pennylane-workflow/
│   ├── cirq-workflow/
│   ├── quantum-algorithms/
│   ├── quantum-problem-framing/
│   ├── quantum-validation/
│   ├── quantum-hardware-execution/
│   ├── quantum-error-mitigation/
│   └── quantum-portability/
├── evals/
│   ├── run.py
│   ├── support/mock_provider.py
│   └── cases/...
├── scripts/
│   ├── new_skill.py
│   ├── skill_lint.py
│   ├── run_snippets.py
│   └── ci.py
├── docs/
│   ├── conventions.md
│   ├── install.md
│   ├── roadmap.md
│   ├── version-matrix.md
│   └── skill-template/
├── openspec/
└── pyproject.toml
```

---

## 9. Mapa de dependencias

```
Etapa 0 ──> Etapa 1 ──> Etapa 2 ──> Etapa 3 ──> Etapa 4 ──> Etapa 5
  harness     hub+qiskit  algoritmos  PennyLane   hardware     release
              validacion  framing     Cirq        mitigacion
                                    ^            portabilidad
                                    |                 ^
                                    +-- cross-framework+
```

Ninguna etapa se cierra sin sus criterios de aceptación. Si una etapa falla su criterio, se ajusta el alcance de esa etapa, no se avanza.

---

## 10. Riesgos globales

| Riesgo | Etapa afectada | Mitigación |
|---|---|---|
| API drift de SDKs | 1, 3, 4 | Versiones pinneadas + `check_env.py` + snippets ejecutados |
| Colisión de triggers | 1, 3, 4 | Lint + evals de routing + revisión global en Etapa 5 |
| Skills demasiado largos | todas | `SKILL.md` ≤ 500 líneas; detalle en `references/` |
| Evals que consumen crédito real | 4 | Mocks obligatorios; dry-run por defecto |
| Windows / wheels | 0, 3 | `uv`, versiones con wheel para 3.12, CI local |
| Duplicación de contenido | 2, 3 | Regla framework=sintaxis / etapa=estrategia |

---

## 11. Primer paso concreto

Si se aprueba A1–A7:

1. Abrir el change `skill-foundation` con `openspec-propose`.
2. Implementar Etapa 0 con `openspec-apply-change`.
3. Al cerrar Etapa 0, proponer `core-quantum-skills` y empezar el corte vertical.

Nada de este plan se implementa desde explore mode: la escritura empieza en la Etapa 0 con el change de OpenSpec.
