# Design

## Context

The repository is empty apart from the six OpenSpec skills under
`.agents/skills/`, the `openspec/` workspace and `docs/roadmap.md`. There is no
Python project, no dependency pinning and no validation tooling. Those six
skills are the only real corpus available, so they double as lint fixtures:
they exercise multi-line descriptions, `references/`-less layouts and code-heavy
bodies.

Constraints that shape the approach:

- Development host is Windows, so every script must avoid shell-specific
  behaviour and use `pathlib`.
- Skills must stay valid without any quantum SDK installed; SDKs are optional
  extras.
- Nothing may require network access or credentials during validation.
- Stage 1 starts immediately after this change, so the tooling must be usable
  from day one, not a framework to be finished later.

## Goals / Non-Goals

**Goals:**

- One canonical way to create a skill, validate it, and prove its snippets run.
- A lint rule set that encodes the conventions in `docs/conventions.md`, so the
  document and the tool cannot drift silently.
- An eval case format stable enough that stage 1 can add cases without changing
  the runner.
- Zero third-party runtime dependencies for the linter beyond YAML parsing.

**Non-Goals:**

- Live model invocation. The eval runner grades recorded answers; capturing them
  is a stage 1 concern. This keeps evals deterministic and offline.
- Automatic fixes (`--fix`). The linter reports, it does not rewrite skills.
- CI aggregation (`scripts/ci.py`), packaging, publishing. Stage 5.
- Any quantum skill, algorithm content or hardware provider.

## Decisions

### D1. `uv` project with dependency extras

`pyproject.toml` declares Python 3.12 and extras `qiskit`, `pennylane`, `cirq`
and `dev`. `uv.lock` pins the full resolution. `uv sync --all-extras` is the
single install command.

Alternatives: `requirements.txt` files per framework (no lock resolution, easy to
drift) and `conda` (heavy for a docs/tooling repo, duplicates Python pinning).
Extras let stage 1 install Qiskit without pulling PennyLane and Cirq.

Version policy: Qiskit is pinned to the 2.4 series because that is the version
observed on this machine (2.4.2) and the API surface stage 1 targets. PennyLane
and Cirq versions are resolved from PyPI at implementation time and pinned
exactly in `uv.lock`; no version is guessed here.

### D2. Three small scripts instead of one multi-command tool

`scripts/new_skill.py`, `scripts/skill_lint.py` and `scripts/run_snippets.py`
are independent entry points, composed later by `scripts/ci.py` (stage 5).

Alternatives: a single `qskill.py` with subcommands (more indirection for three
commands, and one import error breaks everything) and a plugin inside an
existing linter (adds a dependency and hides the rules from the reader).

### D3. Standard library plus PyYAML only

Lint, scaffolding and snippet execution use `argparse`, `pathlib`, `re`,
`subprocess`, `tempfile` and `json`. PyYAML is the only third-party dependency
and lives in the `dev` extra, because both frontmatter and eval cases are YAML.

Alternatives: hand-rolled frontmatter parsing (fragile with multi-line `>`
descriptions, which the OpenSpec skills already use) and TOML via `tomllib`
(no multi-line-friendly mapping for eval checks and inconsistent with the
`SKILL.md` frontmatter that is already YAML).

### D4. Snippet execution in an isolated subprocess

`run_snippets.py` extracts fenced ```` ```python ```` and ```` ```py ```` blocks
and runs each one in a fresh `sys.executable -` subprocess with a 120 s timeout,
`cwd` at the repository root, and captured stdout/stderr.

Alternatives: `exec()` in-process (state leaks between blocks, a hanging block
blocks the runner, a `sys.exit()` kills the lint pass) and a Jupyter-style
kernel (unnecessary dependency).

Marker contract: `# qskill: skip` on the first line of the block marks it as
skipped. It is the only opt-out; no environment-variable detection, so the
result is deterministic on every machine.

### D5. Lint rules and severity

| Rule | Severity | Detail |
|---|---|---|
| layout | error | `SKILL.md` must sit in `.agents/skills/<kebab-id>/` |
| frontmatter | error | `name` and `description` required; `name` equals directory |
| description length | error | 60–500 characters |
| size | error | `SKILL.md` ≤ 500 lines |
| links | error | relative targets inside the skill directory must exist |
| placeholders | error | `TODO`, `FIXME`, `XXX` in `SKILL.md` |
| trigger collision | warning | ≥ 4 shared significant keywords with another skill |

"Significant keyword" means a lowercased token of four or more characters that
is not in a small stopword list. Collisions are warnings because two skills can
legitimately share vocabulary; routing failures are caught by evals in stage 1.
Errors exit 1, warnings exit 0 with a summary line.

Alternatives: embedding-based similarity (needs a model and network) and exact
description equality (misses the real failure mode, near-duplicate triggers).

### D6. Scaffolding from `docs/skill-template/`

`new_skill.py` validates the ID against `^[a-z0-9]+(-[a-z0-9]+)*$`, refuses an
existing target, copies the template tree, and substitutes `{{skill-id}}` in
file contents and `{{Skill Name}}` in the display name.

The template ships a valid description placeholder so the generated skill passes
the linter unchanged, which is the acceptance criterion for scaffolding. Each
real skill then replaces that placeholder with its routing description; this
stage creates no skill, so the design rule about exact `description` frontmatter
is satisfied by defining that placeholder contract.

### D7. Eval cases grade recorded responses

A case is a YAML file under `evals/cases/<skill-id>/` with `id`, `skill`,
`prompt`, `response` (or `response_file`) and `checks`. The runner evaluates the
checks against the recorded `response` and never calls a model.

Check kinds: `required_patterns` and `forbidden_patterns` (regex over the
response), `snippet_runs` (execute the Python blocks of the response the same way
as D4), and `numeric_close` (parse a number from the response and compare with a
tolerance). Results are reported per case and per check; exit 1 if any check
fails.

Alternatives: a live harness with an LLM provider (nondeterministic, needs keys,
cannot run offline) and `promptfoo` (extra runtime, its own config language, and
it still needs recorded or live responses).

### D8. Eval plan for this stage

There are no product eval cases yet. The runner is proven by fixtures:

| Fixture id | What it asserts |
|---|---|
| `fixture-good-skill` | lint exits 0 on a template-generated skill |
| `fixture-bad-frontmatter` | lint reports missing description and name mismatch |
| `fixture-bad-links` | lint reports an unresolved `references/` target |
| `fixture-oversized` | lint reports the 500-line violation |
| `fixture-broken-snippets` | snippet runner reports the failing block and exits 1 |
| `fixture-skipped-block` | snippet runner reports the block as skipped and exits 0 |
| `fixture-eval-pass` / `fixture-eval-fail` | eval runner exits 0 and 1 respectively |

Pass threshold: every fixture produces its expected exit code and expected
message fragment. `evals/run.py --list` on an empty case directory exits 0 and
reports zero cases.

### D9. Directory ownership

```
scripts/     tooling, executable, no import side effects
evals/       runner, schema doc, cases, fixtures
docs/        conventions, template, roadmap, install
.agents/     skills only; tooling never writes here except new_skill.py
```

## Risks / Trade-offs

- **Keyword collision rules produce noise** → warnings only, and the stopword
  list lives beside the rule so it can be tuned in one place.
- **PyYAML dependency contradicts "stdlib only" in spirit** → accepted: both
  frontmatter and eval cases are YAML, and the dependency is dev-only.
- **Snippet subprocess cannot see installed extras in every environment** →
  blocks that need an SDK are expected in stage 1; stage 1 adds SDKs to the dev
  environment or marks blocks `# qskill: skip` with a documented reason.
- **Recorded responses drift from real model output** → the case stores the
  prompt alongside the response, so a stale case is visible in review; stage 1
  re-records cases when a skill's description changes.
- **Windows path casing and separators** → all path handling through `pathlib`,
  comparisons case-insensitive on Windows only.
- **Linter false positives on the OpenSpec skills** (they were not written for
  these rules) → the acceptance criterion is lint-only, and any rule that fails
  on them is either corrected or documented as a known exception in
  `docs/conventions.md`; the rules are not weakened silently.

## Migration Plan

Greenfield: no existing files are rewritten except `README.md`, which gains an
installation and validation section. Rollback is deleting the added files and
restoring `README.md`; no data or service is involved.

## Open Questions

None that affect the specs or the task breakdown. The exact PennyLane and Cirq
version pins are resolved during implementation and recorded in `uv.lock`.
