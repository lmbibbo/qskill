# qskill

Quantum Computing Programming Skills: a suite of agent skills (`SKILL.md`
packages) that teach a coding agent to build quantum projects across Qiskit,
PennyLane and Cirq.

## Status

Stage 0 (foundation) is implemented: the repository ships the environment,
conventions, scaffolding, linter, snippet runner and eval harness. The quantum
skills themselves arrive in stage 1. See [docs/roadmap.md](docs/roadmap.md) for
the staged plan and [docs/conventions.md](docs/conventions.md) for the rules.

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## Install

```bash
uv sync --all-extras
```

Extras: `qiskit`, `pennylane`, `cirq` and `dev` (PyYAML). To work on the tooling
only:

```bash
uv sync --extra dev
```

## Repository layout

```
.agents/skills/     skill packages (SKILL.md + references/scripts/assets)
docs/               conventions, template, roadmap
evals/              eval runner, schema, cases, fixtures
scripts/            linter, scaffolder, snippet runner
openspec/           change proposals and capability specs
```

## Validate

```bash
uv run python scripts/skill_lint.py            # rules from docs/conventions.md
uv run python scripts/run_snippets.py          # executes every ```python block
uv run python evals/run.py --list              # discovered eval cases
uv run python evals/run.py                     # runs the recorded-response evals
```

`skill_lint.py` exits 1 on errors and 0 with warnings only. `run_snippets.py`
and `run.py` exit 1 when something fails.

The full stage 0 validation checklist, including a single copy-paste script that
runs every check, is in
[docs/validation-stage-0.md](docs/validation-stage-0.md).

## Add a skill

```bash
# 1. scaffold from docs/skill-template
uv run python scripts/new_skill.py quantum-project

# 2. replace the placeholder description with 60-500 characters that say
#    when the agent should load it, then write the workflow body

# 3. add detail under references/ (api-map.md, patterns.md, migration.md)

# 4. validate
uv run python scripts/skill_lint.py .agents/skills/quantum-project
uv run python scripts/run_snippets.py .agents/skills/quantum-project
```

A skill is ready when the linter reports no errors, every Python block executes,
and its eval cases pass. Eval cases go in `evals/cases/<skill-id>/`; see
[evals/schema.md](evals/schema.md).

## Self-tests

The tooling is verified with fixtures under `evals/fixtures/`:

```bash
uv run python scripts/skill_lint.py evals/fixtures/lint/bad-frontmatter   # exit 1
uv run python scripts/skill_lint.py evals/fixtures/lint/collision         # exit 0 + warning
uv run python scripts/run_snippets.py evals/fixtures/snippets/broken      # exit 1
uv run python scripts/run_snippets.py evals/fixtures/snippets/skip        # exit 0
uv run python evals/run.py --cases evals/fixtures/evals/pass              # exit 0
uv run python evals/run.py --cases evals/fixtures/evals/fail              # exit 1
```

## Planning

Work is planned with OpenSpec:

```bash
openspec list
openspec status --change skill-foundation
```
