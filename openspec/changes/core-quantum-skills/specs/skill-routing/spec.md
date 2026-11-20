# Spec Delta

## Purpose

Selects which qskill skill an agent loads for a quantum request, and keeps the
hub, the framework skill and the stage skill from answering outside their
boundary.

## ADDED Requirements

### Requirement: Ambiguous and project-level requests load the hub

When a request is project-level or names no concrete API, the agent SHALL load
`quantum-project` before any other qskill skill and SHALL use its decision tree
to choose what to load next. Verified by eval case `routing/ambiguous-task`.
The hub SHALL remain the entry point for requests that mix construction and
validation.

#### Scenario: Starting a project from scratch
- **GIVEN** the user request "Quiero empezar un proyecto cuántico, no sé por dónde empezar"
- **WHEN** the agent routes the request
- **THEN** it loads `quantum-project` and does not load `qiskit-workflow` or
  `quantum-validation` in the same turn

#### Scenario: Mixed construction and validation request
- **GIVEN** the user request "Crea un Bell state y dime si la distribución es correcta"
- **WHEN** the agent routes the request
- **THEN** it loads `quantum-project`, then delegates construction to
  `qiskit-workflow` and the correctness criteria to `quantum-validation`

### Requirement: Framework-specific requests load one framework skill

When a task-level request names Qiskit APIs or asks for Qiskit code, the agent
SHALL load `qiskit-workflow` and answer with Qiskit syntax. Validation criteria
SHALL be linked from `quantum-validation`, not restated. A project-level request
SHALL enter through `quantum-project` even when it names a framework, which then
delegates the syntax. Verified by `routing/qiskit-task` and
`quantum-project/vqe-shape`.

#### Scenario: Concrete Qiskit task
- **GIVEN** the user request "Crea un Bell state en Qiskit y mide 1024 shots"
- **WHEN** the agent routes the request
- **THEN** it loads `qiskit-workflow` and returns Qiskit code for the circuit and
  the measurement

#### Scenario: Project request that names a framework
- **GIVEN** the user request "Quiero montar un proyecto VQE en Qiskit para H2"
- **WHEN** the agent routes the request
- **THEN** it loads `quantum-project` first, classifies the project as
  variational, and delegates Qiskit syntax to `qiskit-workflow`

### Requirement: Validation requests load the stage skill

When a request asks how to verify a circuit or how to interpret results, and
does not ask for framework syntax, the agent SHALL load `quantum-validation`
and SHALL NOT answer with framework API calls. Verified by eval case
`routing/validation-task`.

#### Scenario: Statistical question
- **GIVEN** the user request "¿Cómo compruebo que mi distribución es 50/50 y cuántos shots necesito?"
- **WHEN** the agent routes the request
- **THEN** it loads `quantum-validation` and answers with simulation modes, shot
  counts and tolerances, without returning `QuantumCircuit` code

### Requirement: Delegation keeps a single owner per concern

When a request spans construction and validation, the agent SHALL take framework
syntax only from `qiskit-workflow` and validation criteria only from
`quantum-validation`, and SHALL NOT duplicate either body of knowledge in the
other skill. Verified by the three routing eval cases together.

#### Scenario: Stage knowledge requested inside a framework task
- **GIVEN** a request to build a Qiskit circuit and decide how many shots are enough
- **WHEN** the agent produces the answer
- **THEN** the Qiskit code follows `qiskit-workflow` and the shot-count reasoning
  follows `quantum-validation`, with the two parts clearly separated

### Requirement: Descriptions do not collide

The descriptions of `quantum-project`, `qiskit-workflow` and
`quantum-validation` SHALL share fewer than four significant keywords with each
other pairwise, so the linter reports no trigger-collision warning among them.
Verified by running `scripts/skill_lint.py` over the three skill directories.

#### Scenario: Lint over the stage 1 skills
- **WHEN** the maintainer runs the linter over the three stage 1 skill directories
- **THEN** the run reports zero errors and zero trigger-collision warnings
