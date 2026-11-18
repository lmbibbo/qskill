# Proposal

## Why

The repository has a plan (`docs/roadmap.md`) for a suite of quantum-programming
skills, but no working machinery to build one: no pinned environment, no
conventions, no way to verify that a skill's code samples actually run, and no
eval harness. Without that foundation, every skill would be written by hand and
validated by eye, which is exactly how agent skills rot: outdated APIs,
overlapping trigger descriptions, and pseudocode that never executes.

This change delivers stage 0 of the roadmap so that writing a skill becomes
mechanical and verifiable before any quantum content is authored.

## What Changes

- Add a `uv`-managed Python 3.12 project (`pyproject.toml`, `uv.lock`,
  `.python-version`) with dependency extras for Qiskit, PennyLane, Cirq and dev
  tooling.
- Add `docs/conventions.md` defining skill anatomy, the 500-line limit, the
  mutually exclusive `description` rule, and the "framework owns syntax, stage
  owns strategy" split.
- Add `docs/skill-template/` with a ready-to-copy `SKILL.md`, an
  `api-map.md` stub and a `check_env.py` stub.
- Add `scripts/new_skill.py` to scaffold a skill from the template.
- Add `scripts/skill_lint.py` to validate frontmatter, name/directory match,
  description length and collisions, `SKILL.md` size, local links and leftover
  TODO markers.
- Add `scripts/run_snippets.py` to execute every fenced Python block of a
  `SKILL.md` in an isolated subprocess, with a `# qskill: skip` opt-out for
  blocks that need credentials.
- Add `evals/run.py` plus `evals/schema.md` defining the eval case format
  (`required_patterns`, `forbidden_patterns`, `snippet_runs`, `numeric_close`)
  and a runner that supports `--list` with zero cases.
- Update `README.md` with installation and "how to add / validate a skill".

## Capabilities

### New Capabilities

- `skill-authoring`: the repository contract for creating, structuring and
  validating agent skills: required layout, frontmatter rules, size limits,
  trigger uniqueness, executable-snippet policy, and eval case execution.

### Modified Capabilities

None. There are no existing specs in `openspec/specs/`.

## Impact

- New files: `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`,
  `docs/conventions.md`, `docs/skill-template/**`, `scripts/new_skill.py`,
  `scripts/skill_lint.py`, `scripts/run_snippets.py`, `scripts/snippet_lib.py`
  (shared snippet extraction used by the runner and the eval runner),
  `evals/run.py`, `evals/schema.md`, `evals/cases/.gitkeep`,
  `evals/fixtures/**` (self-test fixtures for the lint, snippet and eval
  tooling).
- Modified files: `README.md`.
- No skill under `.agents/skills/` is created or modified; the six OpenSpec
  skills are used only as fixtures for the linter.
- No runtime service, network access or quantum SDK call is added to tests.

### Out of scope

- Any quantum skill (`quantum-project`, `qiskit-workflow`, etc.) and any eval
  case; those belong to stage 1 and later.
- Framework selection, roadmap changes and `docs/version-matrix.md`.
- CI aggregation (`scripts/ci.py`) and the release tasks of stage 5.
- Hardware providers and credentials; nothing here may require a real backend.

### Acceptance criteria (from roadmap stage 0)

- `uv run python scripts/skill_lint.py .agents/skills` passes over the six
  existing OpenSpec skills.
- `uv run python scripts/new_skill.py demo` generates a skill that the linter
  accepts; the demo skill is then removed.
- `run_snippets.py` reports a failure for a deliberately broken fixture.
- `evals/run.py --list` works with zero cases.
