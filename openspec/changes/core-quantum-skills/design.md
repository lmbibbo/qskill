# Design

## Context

Stage 0 shipped the contract (`docs/conventions.md`, `docs/skill-template/`) and
the harness (`scripts/skill_lint.py`, `scripts/run_snippets.py`, `evals/run.py`).
The repository now has zero quantum skills and zero eval cases: `evals/cases/`
contains only `.gitkeep`. The pinned environment resolves `qiskit==2.4.2` and
`qiskit-aer==0.18.4`.

The harness imposes three hard constraints on this change:

- The eval runner grades a **recorded response**. It never calls a model, so
  routing has to be observable in the recorded text.
- Every `python` fence executes. A skill cannot contain illustrative code.
- `description` collisions are warnings, but stage 1 demands "lint without
  warnings", so the three descriptions must be measured, not guessed.

## Goals / Non-Goals

**Goals:**

- Prove the hub / framework / stage split with three skills that a human can
  follow end to end.
- Classify a project by its deliverable before proposing a layout, so a VQE or
  QUBO project does not inherit a circuit-only skeleton.
- Make routing deterministic and testable with the existing runner, without
  changing `evals/run.py` or `evals/schema.md`.
- Keep framework syntax and validation strategy in separate skills so stage 3
  can reuse `quantum-validation` unchanged for PennyLane and Cirq.

**Non-Goals:**

- Any change to the harness, the template or `skill-authoring`.
- Algorithm content: ansatz families, optimizers, encodings, QUBO→Ising mappings
  and QAOA schedules belong to stage 2. The hub names the shape and defers the
  detail.
- New check kinds, network calls, credentials or hardware jobs.
- Framework choice evidence for PennyLane and Cirq: the matrix exists, but it is
  not validated here.
- Splitting `quantum-validation`; that is a measured reaction, not a design
  assumption.

## Decisions

### Decision 1: Three-skill split and ownership boundaries

| Skill | Owns | Delegates |
|---|---|---|
| `quantum-project` | lifecycle, decision tree, project layout, framework choice, delegation table | all syntax to `qiskit-workflow`; all correctness criteria to `quantum-validation` |
| `qiskit-workflow` | Qiskit 2.x imports, circuit construction, primitives, transpilation, Aer usage, 1.x→2.x traps | shot counts, tolerances, seeds policy, result interpretation |
| `quantum-validation` | simulation mode choice, deterministic checks, statistics, uncertainty reporting | concrete API calls and imports |

Alternative **A** considered: one monolithic `quantum-programming` skill. It
keeps everything in one context window but cannot scale to three frameworks and
would exceed the 500-line limit or push the whole workflow into references that
the agent never loads.

Alternative **B** considered: split `qiskit-workflow` into `qiskit-syntax` and
`qiskit-execution`. The seam is artificial: primitives are part of the same
workflow, and two descriptions would compete for the same triggers.

Alternative **C** considered: fold validation into `qiskit-workflow`. It saves a
skill now but duplicates the statistical method in stage 3, violating the
"framework owns syntax, stage owns strategy" rule in `docs/conventions.md`.

The chosen split wins because validation is the only piece that must survive the
arrival of PennyLane and Cirq unchanged.

### Decision 2: Proposed descriptions (exact frontmatter)

These are the strings to write, each within the 60–500 character window:

- `quantum-project`:
  > Entry point for quantum software projects: identify the project shape
  > (circuit experiment, variational optimization or QUBO), choose the framework
  > and plan the lifecycle. Load when the user starts or reviews a quantum
  > project, compares Qiskit, PennyLane or Cirq, or has not named a concrete
  > deliverable yet.
- `qiskit-workflow`:
  > Build, transpile, simulate and measure circuits with Qiskit 2.x:
  > QuantumCircuit gates, SamplerV2 and EstimatorV2 primitives, qiskit-aer
  > backends and transpiler passes. Use when code must target Qiskit or IBM
  > hardware, or when the request mentions Qiskit imports, primitives or
  > transpilation.
- `quantum-validation`:
  > Verify circuits and results before reporting success: statevector versus
  > shot-based simulation, seeded reproducibility, tolerances, standard error and
  > uncertainty. Use when the request asks whether a circuit is correct, how many
  > shots are needed, or how to test and interpret quantum results.

Measured with the linter's own tokenization, the highest pairwise overlap is two
significant keywords, below the four-keyword threshold. Tasks still rerun
`skill_lint.py` after writing the files, because the threshold is a heuristic,
not a proof.

### Decision 3: Routing evals use an explicit load trace

The runner cannot observe context loading, so each routing case records the
answer prefixed with one line:

```
Loaded skills: qiskit-workflow
```

Checks then assert on that line:

- `required_patterns: ["Loaded skills: [^\\n]*qiskit-workflow"]`
- `forbidden_patterns: ["Loaded skills: [^\\n]*(quantum-validation|quantum-project)"]`

plus a content assertion that proves the answer really belongs to that skill
(for example `QuantumCircuit` for the Qiskit case). The trace is a recording
convention documented in the eval case, not a runner feature. Alternative
considered: infer routing from answer content alone. It is more realistic but
cannot distinguish "loaded the hub and delegated" from "answered directly".

### Decision 4: Eval plan

Eleven cases, graded by `evals/run.py`. The roadmap floor is **≥ 8/10**; with the
added project-shape case the suite is eleven cases, so the operative threshold
is **≥ 9/11** (≥ 80 %). Because routing is the point of the stage, all three
routing cases must be green before the stage closes; if one fails, the fix is a
description change, not a lower threshold.

| Case id | Asserts | Checks |
|---|---|---|
| `routing/qiskit-task` | Qiskit request loads only `qiskit-workflow` | load trace, `QuantumCircuit` present |
| `routing/validation-task` | statistics request loads only `quantum-validation` | load trace, no `QuantumCircuit`, mentions shots/error |
| `routing/ambiguous-task` | project-level request loads only `quantum-project` | load trace, lifecycle/delegation vocabulary |
| `quantum-project/vqe-shape` | a VQE project is classified as variational, not circuit | load trace, variational vocabulary, no `QuantumCircuit` or Qiskit API call |
| `qiskit-workflow/bell-state` | Bell circuit is complete and runnable | `h(0)`, `cx(0, 1)`, measurements, `snippet_runs` |
| `qiskit-workflow/transpile-line` | transpiles to a constrained line target | `transpile`/`generate_preset_pass_manager`, `seed_transpiler`, basis/coupling, `snippet_runs` |
| `qiskit-workflow/sampler-v2` | samples 1024 shots through a primitive | `StatevectorSampler`/`SamplerV2`, `shots=1024`, no `execute(`, `snippet_runs` |
| `qiskit-workflow/reject-old-api` | refuses `execute()` and `BasicAer` | forbidden patterns, replacement named |
| `quantum-validation/bell-distribution` | 50/50 within 0.05 at 1024 shots | `numeric_close` on 0.5 ± 0.05, standard-error wording, `snippet_runs` |
| `quantum-validation/ghz-state` | GHZ amplitudes only on `000`/`111` | required patterns, `numeric_close` 0.5, `snippet_runs` |
| `quantum-validation/seed-reproducibility` | same seed gives identical counts | `snippet_runs` where the snippet runs twice and asserts equality |

`numeric_close` uses the first number by default, so both validation cases pass
an explicit `pattern` with a capture group to avoid matching a shot count.

Validation cases must respect the stage/framework boundary: their recorded
responses use framework-neutral Python (statistics over a counts dictionary)
and never import a quantum SDK. The Qiskit snippets that produce those counts
belong to `qiskit-workflow` and its cases. `quantum-project` ships no Python
block at all; its `check_env.py` reports the Python version and which optional
SDK extras are present.

### Decision 5: Version pins

`qiskit>=2.4,<2.5` and `qiskit-aer>=0.17` stay as they are in `pyproject.toml`;
the lock resolves 2.4.2 and 0.18.4. The lower bound is the first minor that
carries the stable 2.x primitive surface this skill teaches, and the 1.x
execution APIs the skill rejects were removed in 2.0. The upper bound keeps API
drift out of a stage whose snippets are executable. `qiskit-aer` is required
because `StatevectorSampler` with shots needs a local Aer provider; version
0.17 is the floor declared for Qiskit 2.4 compatibility. No new dependency is
added by this change.

### Decision 6: Project shape is a first-class hub concern

The hub classifies the project by its **deliverable** before it proposes a
skeleton. "Start a quantum project" is not one shape:

| Shape | Deliverable | Own files | Success metric |
|---|---|---|---|
| circuit | a prepared state or a distribution | circuit + measurement | amplitudes or counts within tolerance |
| variational (VQE/QAOA) | a minimized energy or cost | ansatz, Hamiltonian, optimizer loop | energy vs a classical reference within tolerance |
| optimization (QUBO) | a feasible binary solution | QUBO model, Ising mapping/embedding, solver | feasibility plus approximation ratio |

What is shared by all three lives in `project-layout.md`: pinned environment,
`src/` + `tests/` + `scripts/`, explicit seeds and the hand-off to
`quantum-validation`. What varies lives in `project-shapes.md`. The hub is the
only place that knows the mapping shape → skeleton.

Alternative **B** considered: keep the hub generic and let stage 2 ship the
skeletons. It is cheaper now, but leaves the hub with nothing to say beyond
"create `src/`", which is exactly the gap this decision closes.

Alternative **C** considered: author the VQE and QUBO structures in full here.
It breaks the one-change-per-stage rule and will be rewritten when
`quantum-algorithms` lands.

The hub must also win the routing race when a project request names a framework
("montar un proyecto VQE en Qiskit"): `skill-routing` treats project-level
requests as hub-first even when a framework is named, and the hub delegates the
syntax afterwards.

## Risks / Trade-offs

- [The hub and validation descriptions still collide in practice] → Measure with
  the linter and the three routing evals; tune wording before closing. Split
  `quantum-validation` only if the measured overlap persists.
- [Sampler snippets are slow or flaky at 1024 shots] → Use two-qubit circuits,
  local Aer, fixed seeds; the 120 s per-block timeout is ample.
- [A routing trace line is unrealistic] → Pair every trace assertion with a
  content assertion, so a case cannot pass on the trace alone.
- [500-line limit pressure in `qiskit-workflow`] → API map, patterns and the
  1.x→2.x migration note live in `references/`; `SKILL.md` stays a workflow.
- [Stage 0 harness gaps appear mid-implementation] → Record them as follow-ups;
  this change is not allowed to modify the harness.
- [The hub drifts into stage 2 algorithm content] → `project-shapes.md` names
  files, metrics and hand-offs only; the VQE eval fails if the hub returns
  Qiskit API calls or ansatz implementation instead of a classification.

## Migration Plan

Additive change, no migration. Creation order is `qiskit-workflow` and
`quantum-validation` first, then `quantum-project`, because the hub links to the
other two and the linter fails on unresolved links. `README.md` and the stage
status in `docs/roadmap.md` are updated only when the acceptance criteria pass.
