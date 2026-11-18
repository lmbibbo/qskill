# Eval case format

An eval case is a YAML file under `evals/cases/<skill-id>/`. The runner grades a
**recorded response**; it never calls a model and never uses the network. This
keeps results deterministic and lets the suite run offline.

## Fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | unique case id within the skill, kebab-case |
| `skill` | yes | skill ID the case belongs to; must match its directory |
| `prompt` | yes | the user request that produced the recorded response |
| `response` | one of | recorded model answer, inline |
| `response_file` | one of | path to a recorded answer, relative to the case file |
| `checks` | yes | non-empty list of checks |

Exactly one of `response` and `response_file` must be present.

```yaml
id: bell-state
skill: qiskit-workflow
prompt: |
  Build a Bell state with Qiskit 2.x and sample 1024 shots.
response: |
  ```python
  from qiskit import QuantumCircuit
  from qiskit.primitives import StatevectorSampler

  circuit = QuantumCircuit(2)
  circuit.h(0)
  circuit.cx(0, 1)
  circuit.measure_all()
  print(StatevectorSampler().run([circuit], shots=1024).result()[0].data.meas.get_counts())
  ```
checks:
  - kind: required_patterns
    patterns: ["StatevectorSampler"]
  - kind: forbidden_patterns
    patterns: ["execute\\(", "BasicAer"]
  - kind: snippet_runs
```

## Checks

### `required_patterns`

Every pattern is a Python regular expression that must match somewhere in the
response. Missing patterns fail the case.

```yaml
- kind: required_patterns
  patterns: ["QuantumCircuit", "SamplerV2|StatevectorSampler"]
```

### `forbidden_patterns`

Every pattern must be absent. A match fails the case; use it for removed APIs
and anti-patterns.

```yaml
- kind: forbidden_patterns
  patterns: ["execute\\(", "qiskit\\.BasicAer"]
```

### `snippet_runs`

Extracts every fenced `python`/`py` block from the response and executes each one
with the same rules as `scripts/run_snippets.py`: isolated subprocess, 120 second
timeout, working directory at the repository root. Blocks marked
`# qskill: skip` are ignored. A response with no Python block fails the case.

```yaml
- kind: snippet_runs
```

### `numeric_close`

Extracts a number from the response and compares it with a target inside a
tolerance. By default the first number in the response is used; `pattern` can
select a specific one, and its first group is used when present.

```yaml
- kind: numeric_close
  target: -1.137
  tolerance: 0.05
  pattern: "energy\\s*=\\s*([-+]?\\d+\\.\\d+)"
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | every case passed, or `--list` was used |
| 1 | at least one check failed |
| 2 | usage error, such as a missing cases directory or malformed case |
