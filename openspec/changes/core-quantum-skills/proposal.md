# Proposal

## Why

Stage 0 proved a skill can be scaffolded, linted, executed and graded, but the
repository ships no quantum content. Stage 1 tests the format, the harness and
the routing contract with three real skills before the suite grows. If the
hub/framework/stage split fails here, it will fail later.

## What Changes

- Add the hub skill `quantum-project`: lifecycle, decision tree, delegation
  table and a layout that distinguishes circuit, variational and QUBO projects.
- Add the framework skill `qiskit-workflow`: Qiskit 2.x imports, primitives,
  circuit construction, transpilation and execution.
- Add the stage skill `quantum-validation`: simulation modes, deterministic
  tests, statistics and how to report uncertainty.
- Add the matching `references/` files and a `scripts/check_env.py` per skill.
- Add eleven eval cases: three routing, four Qiskit, three validation and one
  project-shape case, run through the existing recorded-response runner.
- Update `README.md` and the stage status in `docs/roadmap.md` when the stage
  closes.

Roadmap stage: **Etapa 1 — Corte vertical** (`docs/roadmap.md` §3).

## Capabilities

### New Capabilities

- `skill-routing`: how the agent chooses among the hub, framework and stage
  skills, including the delegation contract and the description triggers that
  make routing deterministic.
- `framework-qiskit`: the Qiskit 2.x API surface an agent must use to build,
  transpile, simulate and measure circuits, and the removed-API behaviour it
  must avoid.
- `circuit-validation`: how a circuit or result is checked before it is
  reported: simulation modes, deterministic seeding, tolerances and statistical
  uncertainty.
- `project-structure`: how the hub classifies a quantum project by its
  deliverable, the skeleton and success metric each shape gets, and the
  invariants every shape shares.

### Modified Capabilities

None. `skill-authoring` defines the repository contract and is not changing;
this change consumes it.

## Impact

- New directories: `.agents/skills/quantum-project/`,
  `.agents/skills/qiskit-workflow/`, `.agents/skills/quantum-validation/`.
- Hub references: `lifecycle.md`, `framework-choice.md`, `project-shapes.md`
  (the three skeletons) and `project-layout.md` (the shared invariants).
- New eval cases under `evals/cases/routing/`, `evals/cases/quantum-project/`,
  `evals/cases/qiskit-workflow/` and `evals/cases/quantum-validation/`.
- Modified files: `README.md`, `docs/roadmap.md` (stage status at close).
- No change to `scripts/`, `evals/run.py`, `evals/schema.md` or the skill
  template. If a tool gap appears during implementation, it is recorded as a
  follow-up instead of being fixed inside this change.
- No network, credentials or hardware jobs: every snippet and eval runs locally.

### Out of scope

- PennyLane and Cirq skills, cross-framework equivalence and the multi-SDK
  matrix: stage 3.
- `quantum-algorithms` and `quantum-problem-framing`: stage 2. That covers
  ansatz families, optimizers, encodings, QUBO→Ising mappings and QAOA. Stage 1
  classifies shapes only.
- Hardware execution, error mitigation and portability: stage 4.
- Splitting `quantum-validation` into two skills: only if the routing evals
  show trigger collisions, and only after measuring.
- CI aggregation (`scripts/ci.py`), `docs/version-matrix.md` and the release
  tasks of stage 5.

### Acceptance criteria (from roadmap stage 1)

- At least 80 % of evals green (8/10 roadmap floor; 9/11 with the added
  project-shape case).
- 100 % of snippets execute in a clean virtual environment.
- Lint without warnings.
- A human reads the three `SKILL.md` files and can follow the flow without
  asking questions.
