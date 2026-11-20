# Spec Delta

## Purpose

Defines the Qiskit 2.x API surface an agent must use to build, transpile,
simulate and measure circuits, and the removed 1.x APIs it must refuse in favour
of their replacements.

## ADDED Requirements

### Requirement: Target SDK version range

The skill SHALL target `qiskit>=2.4,<2.5` with `qiskit-aer>=0.17`, SHALL state
that range in `SKILL.md`, and SHALL fail its environment check when the
installed Qiskit version is outside the range. Verified by running
`scripts/check_env.py` in the pinned environment and by eval case
`qiskit-workflow/sampler-v2`.

#### Scenario: Environment matches the pinned range
- **WHEN** `scripts/check_env.py` runs with `qiskit` 2.4.x installed
- **THEN** it prints the Qiskit and Aer versions and exits 0

#### Scenario: Environment is outside the range
- **WHEN** `scripts/check_env.py` runs with no Qiskit installation
- **THEN** it exits non-zero and prints the command that installs the SDK, such
  as `uv sync --extra qiskit`

### Requirement: Removed 1.x APIs are rejected

When a request would produce code that uses APIs removed in Qiskit 2.0, the
agent SHALL use the 2.x replacement instead: primitives (`StatevectorSampler`,
`SamplerV2`, `EstimatorV2`) instead of `execute()`, and `qiskit_aer` instead of
`qiskit.BasicAer`. Verified by eval case `qiskit-workflow/reject-old-api`.

#### Scenario: User asks for the old execution API
- **GIVEN** the user request "usa execute() con BasicAer para correr el circuito"
- **WHEN** the agent answers
- **THEN** it explains that both APIs were removed in Qiskit 2.0 and returns a
  snippet that uses `StatevectorSampler` or `SamplerV2`
- **AND** the recorded response matches neither `execute\(` nor `BasicAer`

### Requirement: Circuits are built with the 2.x object model

The agent SHALL build circuits with `QuantumCircuit` and standard gates, SHALL
include measurements when a sampled result is requested, and SHALL return a
complete runnable program rather than a fragment. Verified by eval case
`qiskit-workflow/bell-state`.

#### Scenario: Bell state with measurements
- **GIVEN** the user request "Crea un Bell state en Qiskit y mide 1024 shots"
- **WHEN** the agent answers
- **THEN** the response contains a `QuantumCircuit(2)` with `h(0)`, `cx(0, 1)`
  and measurements, and the snippet runs end to end

### Requirement: Execution goes through primitives

The agent SHALL execute circuits with `SamplerV2` or `StatevectorSampler` for
bitstring sampling and with `EstimatorV2` for expectation values, SHALL pass an
explicit shot count, and SHALL read results from the primitive result object.
Verified by eval case `qiskit-workflow/sampler-v2`.

#### Scenario: Sampled execution with an explicit shot count
- **GIVEN** a request to sample a circuit with 1024 shots
- **WHEN** the agent answers
- **THEN** it instantiates a sampler, calls `run` with `shots=1024`, and reads
  `data.meas.get_counts()` from the result

### Requirement: Transpilation targets the declared constraints

When the target backend, basis gates or coupling map is known, the agent SHALL
transpile with `transpile` or `generate_preset_pass_manager`, SHALL state the
optimization level it uses, and SHALL set `seed_transpiler` so the output is
reproducible. Verified by eval case `qiskit-workflow/transpile-line`.

#### Scenario: Transpiling to a line coupling map
- **GIVEN** a request to run a circuit on a backend with a line coupling map
- **WHEN** the agent answers
- **THEN** it transpiles with an explicit seed and the resulting circuit uses
  only the declared basis gates and respects the coupling map

### Requirement: The skill ships an environment check

The skill directory SHALL contain `scripts/check_env.py`, which SHALL verify
Python 3.12, the Qiskit version range and the critical imports, and SHALL exit
non-zero with an actionable message when a check fails. Verified by running the
script in a clean virtual environment.

#### Scenario: Critical import is missing
- **WHEN** `scripts/check_env.py` runs without `qiskit_aer` installed
- **THEN** it names the missing package, prints the install command, and exits
  non-zero
