# Skill conventions

This document is the contract that `scripts/skill_lint.py` enforces. If a rule
changes here, the linter changes in the same commit; if the linter changes, this
document changes with it.

## Anatomy

```
.agents/skills/<skill-id>/
├── SKILL.md          # required: routing description + workflow
├── references/       # optional: detail loaded on demand
├── scripts/          # optional: helper scripts used by the skill
└── assets/           # optional: templates copied into a project
```

- `<skill-id>` matches `^[a-z0-9]+(-[a-z0-9]+)*$` and is unique in the repo.
- The directory name is the skill ID. The frontmatter `name` is only a display
  label, but the linter requires it to match the directory when normalized
  (case-insensitive, with `-` and `_` treated as spaces).
- Every file a `SKILL.md` links to with a relative path must exist.

## SKILL.md

```yaml
---
name: Qiskit Workflow
description: >
  Build, transpile, simulate and measure circuits with Qiskit 2.x. Use when a
  project targets Qiskit or IBM Quantum, or when the task mentions
  QuantumCircuit, transpile, SamplerV2, EstimatorV2 or qiskit-aer.
license: MIT
---
```

- `description` is 60–500 characters and states **when** to load the skill, not
  what the skill contains.
- The body starts with when to use the skill, then the workflow, then pitfalls,
  then links to `references/`.
- `SKILL.md` stays at or below **500 lines**. Anything longer is detail that
  belongs in `references/`, which the agent reads only when needed.

## Descriptions must not collide

Two skills whose descriptions share four or more significant keywords are
reported as a possible routing collision.

- A significant keyword is a lowercased token of four or more characters that is
  not in the stopword list inside `scripts/skill_lint.py`.
- Collisions are **warnings**, not errors: two skills can legitimately share
  vocabulary. Routing failures are caught by eval cases, not by the linter.

## Framework skills vs stage skills

| Kind | Owns | Example |
|---|---|---|
| framework | API syntax, imports, primitives, version notes | `qiskit-workflow` |
| stage | strategy, decision criteria, cross-framework method | `quantum-validation` |

A framework skill never explains when an algorithm is appropriate; a stage skill
never shows framework-specific API calls. When stage knowledge is needed by a
framework skill, it links to the stage skill instead of repeating it.

## Executable snippets

Every fenced `python` or `py` block inside a `SKILL.md` is executed by
`scripts/run_snippets.py`. There is no "illustrative" Python.

- Execution is isolated: one subprocess per block, 120 second timeout, working
  directory at the repository root.
- A block that needs credentials, network access or real hardware starts with
  `# qskill: skip` on its first line and explains why in the line above the
  fence. Skipped blocks are reported, never executed.
- Blocks must be deterministic. No random seeds left to chance, no wall-clock
  dependent assertions, no writes outside the temporary directory.

## Lint rules

| Rule | Severity | Detail |
|---|---|---|
| `layout` | error | `<skill-id>` directory must be kebab-case |
| `frontmatter` | error | `name` and `description` required; `name` matches the directory |
| `description-length` | error | 60–500 characters |
| `size` | error | `SKILL.md` at most 500 lines |
| `link` | error | relative targets inside the skill directory must exist |
| `placeholder` | error | no `TODO`, `FIXME` or `XXX` in `SKILL.md` |
| `trigger-collision` | warning | four or more shared significant keywords |

Rules marked as errors exit with status 1. Warnings exit 0 and print a summary.

## Eval cases

Eval cases live in `evals/cases/<skill-id>/*.yaml` and follow
[`evals/schema.md`](../evals/schema.md). The runner grades a recorded response;
it never calls a model and never touches the network.

## Self-tests and fixtures

The tooling is tested with fixtures rather than a test framework:

| Fixture | Exercises |
|---|---|
| `evals/fixtures/lint/bad-frontmatter` | missing description, name mismatch |
| `evals/fixtures/lint/bad-links` | unresolved `references/` target |
| `evals/fixtures/lint/oversized` | 500-line limit |
| `evals/fixtures/lint/bad-name` | non-kebab directory name |
| `evals/fixtures/lint/collision` | trigger-collision warning |
| `evals/fixtures/snippets/broken` | failing snippet, non-zero exit |
| `evals/fixtures/snippets/skip` | `# qskill: skip` handling |
| `evals/fixtures/evals/pass` | eval case that must pass |
| `evals/fixtures/evals/fail` | eval case that must fail |

Run them with the commands in `README.md`.

## Known exceptions

The six OpenSpec skills predate these rules. When the linter reports something
on them that is not worth changing (for example a description outside the length
window), record it here with the reason. Rules are not weakened silently.

- `trigger-collision` warnings between `openspec-*` skills are expected. They
  share the OpenSpec vocabulary (`openspec`, `opsx`, `change`) by design, and
  their routing is governed by the slash command or skill name the user picks,
  not by keyword matching alone. Filter with `2>&1 | Select-String -NotMatch
  "trigger-collision"` when the noise is distracting.
- `docs/skill-template/SKILL.md` is intentionally excluded from lint runs: its
  display name is a `{{Skill Name}}` placeholder, so it only validates after
  `scripts/new_skill.py` substitutes it.
