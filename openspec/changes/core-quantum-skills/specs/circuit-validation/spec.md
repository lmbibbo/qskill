# Spec Delta

## Purpose

Defines how an agent proves that a circuit or a result is correct before it
reports success: which simulation mode to use, how many shots are enough, how
to make a check reproducible, and how to state uncertainty.

## ADDED Requirements

### Requirement: Exact checks use statevector simulation

When the expected output is exact and the circuit is small enough to simulate,
the agent SHALL validate with statevector simulation and compare amplitudes or
probabilities directly, rather than inferring correctness from sampled counts.
Verified by eval case `quantum-validation/ghz-state`.

#### Scenario: Three-qubit GHZ state
- **GIVEN** a three-qubit GHZ circuit and a statevector simulator
- **WHEN** the agent validates the prepared state
- **THEN** it reports that only `|000>` and `|111>` have non-zero amplitude, each
  with probability 0.5 within 1e-6

### Requirement: Sampled checks declare a statistical tolerance

When the result is sampled, the agent SHALL state the shot count, the expected
distribution and a tolerance derived from the standard error, and SHALL NOT
claim exact equality. Verified by eval case
`quantum-validation/bell-distribution`.

#### Scenario: Bell distribution with 1024 shots
- **GIVEN** a Bell circuit sampled with 1024 shots
- **WHEN** the agent validates the counts
- **THEN** it checks that each of `00` and `11` is 0.5 within a 0.05 tolerance
  and explains that the tolerance is about three standard errors

### Requirement: Validation is reproducible

The agent SHALL set explicit seeds on every simulator and transpiler used in a
check, and SHALL show how to rerun it. Two runs with the same seed SHALL produce
identical counts. Verified by eval case
`quantum-validation/seed-reproducibility`.

#### Scenario: Same seed, same counts
- **GIVEN** a circuit executed twice with `seed=7`
- **WHEN** both runs complete
- **THEN** the two count dictionaries are identical

#### Scenario: Unseeded execution is not a valid check
- **GIVEN** a validation snippet that relies on the default simulator seed
- **WHEN** the agent reviews it
- **THEN** it adds an explicit seed before presenting the result as reproducible

### Requirement: Results report their uncertainty

The agent SHALL attach an uncertainty to every reported measured quantity: a
standard error or confidence interval for probabilities, and a standard
deviation for expectation values. It SHALL state when an observed deviation is
within noise. Verified by eval cases `quantum-validation/bell-distribution` and
`quantum-validation/ghz-state`.

#### Scenario: Deviation within noise
- **GIVEN** a Bell run where `00` appears with frequency 0.48 at 1024 shots
- **WHEN** the agent reports the result
- **THEN** it states the standard error and concludes that 0.48 is consistent
  with 0.5 rather than reporting a bias

### Requirement: Success is reported only after a check runs

When the agent finishes building or fixing a circuit, it SHALL run a validation
check and SHALL report the check output alongside the claim of correctness.
Verified by all stage 1 validation eval cases and by
`qiskit-workflow/bell-state`.

#### Scenario: Claiming a working Bell state
- **GIVEN** a freshly written Bell-state program
- **WHEN** the agent is about to report that the program works
- **THEN** it first executes the program or its validation snippet and includes
  the observed counts and the pass criterion in the answer
