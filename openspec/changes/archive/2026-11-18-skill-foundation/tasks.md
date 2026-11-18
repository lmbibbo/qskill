# Tasks

## 1. Environment

- [x] 1.1 Create `pyproject.toml` for Python 3.12 with extras `qiskit`,
  `pennylane`, `cirq` and `dev` (PyYAML); verify `uv sync --all-extras` succeeds
  and `uv.lock` is generated
- [x] 1.2 Add `.python-version` with `3.12` and `.gitignore` covering `.venv/`,
  `__pycache__/`, `*.pyc` and temp snippet artifacts; verify `git status` lists
  only the intended files
- [x] 1.3 Verify the tooling environment is self-sufficient: with only the `dev`
  extra installed, `uv run python -c "import yaml; print(yaml.__version__)"`
  succeeds and no quantum SDK import is required

## 2. Conventions and template

- [x] 2.1 Write `docs/conventions.md` covering skill anatomy, the 500-line rule,
  the description contract (60–500 characters, mutually exclusive triggers),
  the framework-vs-stage split, the executable-snippet policy and the
  `# qskill: skip` marker; verify every lint rule in design §D5 has a matching
  section
- [x] 2.2 Create `docs/skill-template/SKILL.md` using `{{skill-id}}` and
  `{{Skill Name}}` placeholders with a description that satisfies the linter, and
  verify it stays at or below 500 lines
- [x] 2.3 Add `docs/skill-template/references/api-map.md` and
  `docs/skill-template/scripts/check_env.py` stubs; verify the file set matches
  the scaffolding contract in design §D6

## 3. Linter

- [x] 3.1 Implement layout, frontmatter parsing, name/directory match and
  description-length rules in `scripts/skill_lint.py`; verify it runs against
  `.agents/skills` and reports the six OpenSpec skills with exit code 0 or with
  exceptions documented in `docs/conventions.md`
- [x] 3.2 Add the size, local-link and placeholder rules; verify the
  `fixture-oversized`, `fixture-bad-links` and `fixture-bad-frontmatter` fixtures
  each exit non-zero and name the violated rule
- [x] 3.3 Add the trigger-collision warning with a stopword list kept next to the
  rule; verify two fixture skills sharing four or more keywords produce a warning
  while the run still exits 0
- [x] 3.4 Verify the CLI contract: `--help` works, a clean run prints a per-skill
  summary, errors exit 1 and warnings exit 0

## 4. Scaffolder

- [x] 4.1 Implement `scripts/new_skill.py` with ID validation against
  `^[a-z0-9]+(-[a-z0-9]+)*$`, template copying and `{{ }}` substitution; verify
  `uv run python scripts/new_skill.py demo` creates the three template files
- [x] 4.2 Verify the generated `demo` skill passes `scripts/skill_lint.py`; then
  remove the demo directory
- [x] 4.3 Verify both refusal paths: an existing target directory and an invalid
  ID each exit non-zero and change nothing

## 5. Snippet runner

- [x] 5.1 Implement fenced-block extraction for `python` and `py` with the
  `# qskill: skip` marker in `scripts/run_snippets.py`; verify block counts and
  skip detection against a fixture with mixed blocks
- [x] 5.2 Implement isolated subprocess execution with a 120 s timeout, `cwd` at
  the repository root and captured output; verify `fixture-broken-snippets` exits
  1 and reports file, block order and stderr
- [x] 5.3 Verify `fixture-skipped-block` exits 0 and lists the block as skipped,
  and that running the runner over the six OpenSpec skills completes without
  failing

## 6. Eval runner

- [x] 6.1 Write `evals/schema.md` documenting `id`, `skill`, `prompt`,
  `response`/`response_file`, `checks`, and the four check kinds; verify it
  matches the implementation added in this group
- [x] 6.2 Implement YAML case discovery under `evals/cases/<skill-id>/` with
  `--list`, `--skill` filtering and per-case reporting in `evals/run.py`; verify
  `--list` on an empty cases directory exits 0 and reports zero cases
- [x] 6.3 Implement the `required_patterns`, `forbidden_patterns` and
  `numeric_close` checks; verify `fixture-eval-pass` exits 0 and
  `fixture-eval-fail` exits 1 naming the failing check
- [x] 6.4 Implement `snippet_runs` reusing the design §D4 execution semantics;
  verify a passing and a failing response fixture produce the expected exit codes
- [x] 6.5 Verify offline operation: no network module is imported by the runner
  and its fixtures, and every fixture result is deterministic across two runs

## 7. Documentation

- [x] 7.1 Update `README.md` with installation (`uv sync --all-extras`), the
  validation commands and a step-by-step "add a skill" walkthrough; verify each
  command runs as written
- [x] 7.2 Document the fixture layout and any accepted lint exceptions in
  `docs/conventions.md`; verify a reader can map each fixture to the rule it
  exercises

## 8. Integration verification

- [x] 8.1 Run the four acceptance commands from `proposal.md` in order and record
  their exit codes in the change notes; verify all four behave as specified
- [x] 8.2 Verify `git status` contains only the files listed in the proposal's
  Impact section, plus the change artifacts, and that no quantum SDK is required
  for the lint pass

## Workflow follow-up

- Archive this change after review, following the archive guidance in
  `openspec/config.yaml`.
