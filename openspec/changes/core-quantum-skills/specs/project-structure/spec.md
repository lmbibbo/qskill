# Spec Delta

## Purpose

Classifies a quantum project by the deliverable it must produce, and gives each
shape the skeleton and success metric it needs without teaching the algorithm
itself.

## ADDED Requirements

### Requirement: Project shape is classified before a layout

When a request is project-level, the agent SHALL determine the deliverable — a
prepared state or distribution, a minimized energy or cost, or a feasible binary
solution — and SHALL classify the project as circuit, variational or
optimization before proposing any layout. When the deliverable cannot be
determined, the agent SHALL state the assumption and ask one distinguishing
question. Verified by eval case `quantum-project/vqe-shape`.

#### Scenario: Variational project seed
- **GIVEN** the user request "Quiero montar un proyecto para calcular la energía de H2 con VQE"
- **WHEN** the agent classifies the project
- **THEN** it selects the variational shape and states that the deliverable is
  an energy value

#### Scenario: Optimization project seed
- **GIVEN** the user request "Quiero resolver un problema de asignación con QUBO"
- **WHEN** the agent classifies the project
- **THEN** it selects the optimization shape and states that the deliverable is a
  feasible binary solution

#### Scenario: Deliverable is unclear
- **GIVEN** the user request "Quiero hacer algo con computación cuántica"
- **WHEN** the agent classifies the project
- **THEN** it starts from the smallest circuit experiment, says so explicitly,
  and asks whether the goal is a state, an optimized value or a binary solution

### Requirement: Each shape has its own skeleton and success metric

The hub SHALL give each shape a distinct skeleton and success metric: circuit
(circuit plus measurement; amplitudes or counts), variational (ansatz,
Hamiltonian and optimizer loop; energy against a classical reference) and
optimization (QUBO model, Ising mapping or embedding and solver; feasibility
plus approximation ratio). Verified by review of `references/project-shapes.md`
and by eval case `quantum-project/vqe-shape`.

#### Scenario: Variational skeleton
- **WHEN** the agent lays out a variational project
- **THEN** the skeleton names an ansatz module, a Hamiltonian module, an
  optimizer loop and an energy tolerance

#### Scenario: Circuit skeleton stays minimal
- **WHEN** the agent lays out a circuit project
- **THEN** the skeleton contains no optimizer loop and no Hamiltonian module

### Requirement: All shapes share the same invariants

The three skeletons SHALL share one invariant core: pinned Python and SDK
versions, `src/` plus `tests/` plus `scripts/`, explicit seeds, and validation
delegated to `quantum-validation`. Verified by review of
`references/project-layout.md` against the three entries of
`references/project-shapes.md`.

#### Scenario: Shared invariants are present in every skeleton
- **WHEN** the agent presents any of the three skeletons
- **THEN** the same environment, test layout, seed policy and validation hand-off
  are included, and only the shape-specific modules differ

### Requirement: Algorithm detail is deferred, not duplicated

When a shape needs ansatz, optimizer, encoding, embedding or schedule choices,
the agent SHALL name them as deferred to the algorithm capability of stage 2 and
SHALL NOT provide their implementation from the hub. Verified by eval case
`quantum-project/vqe-shape`, whose recorded response must contain no Qiskit API
call.

#### Scenario: VQE request at the hub
- **GIVEN** a project-level VQE request
- **WHEN** the agent answers from the hub
- **THEN** it names the variational skeleton and says the ansatz and optimizer
  choice arrive with stage 2, without returning `QuantumCircuit` code
