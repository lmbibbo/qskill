# skill-authoring Specification

## Purpose

Defines the repository contract for authoring agent skills: where a skill lives,
what its frontmatter and size must satisfy, how its code samples are proven to
execute, and how eval cases are declared and run. It exists so that every skill
in the suite is created and validated the same way.

## Requirements

### Requirement: Skill layout

Every skill SHALL be a directory under `.agents/skills/<skill-id>/` containing a
`SKILL.md`, and MAY contain `references/`, `scripts/` and `assets/`
subdirectories. The skill ID SHALL be the directory name in kebab-case and SHALL
be unique across the repository.

#### Scenario: A well-formed skill is accepted
- **WHEN** a contributor runs `python scripts/skill_lint.py .agents/skills`
- **THEN** every discovered skill directory with a `SKILL.md` is checked and the
  command exits 0 if all of them satisfy the layout

#### Scenario: A misfiled skill is reported
- **WHEN** a `SKILL.md` exists outside a skill directory, or a skill directory
  name is not kebab-case
- **THEN** the linter reports the offending path with the violated layout rule
  and exits non-zero

### Requirement: Frontmatter contract

The linter SHALL require `name` and `description` in each `SKILL.md`
frontmatter, SHALL require the display name to match the skill directory, SHALL
require the description to be between 60 and 500 characters, and SHALL flag
descriptions that collide with another skill.

#### Scenario: Missing or malformed frontmatter
- **WHEN** a `SKILL.md` has no `description`, or a `name` that differs from its
  directory, or a description outside the allowed length
- **THEN** the linter reports the file, the rule and the observed value, and the
  run fails

#### Scenario: Overlapping triggers are surfaced
- **WHEN** two skills declare descriptions that share four or more significant
  keywords
- **THEN** the linter reports both skill IDs as a possible routing collision
  without failing the run

### Requirement: Skill size limit

A `SKILL.md` SHALL NOT exceed 500 lines, so that detail lives in `references/`
files loaded on demand.

#### Scenario: Oversized skill is rejected
- **WHEN** a `SKILL.md` has 501 lines or more
- **THEN** the linter reports the line count and the file, and the run fails

### Requirement: Local references resolve

Every relative link in a `SKILL.md` that points to a file inside the skill
directory SHALL resolve to an existing file.

#### Scenario: Broken reference
- **WHEN** a `SKILL.md` links to `references/api-map.md` but that file does not
  exist
- **THEN** the linter reports the broken target and exits non-zero

### Requirement: Executable snippets

`scripts/run_snippets.py` SHALL extract every fenced `python` block from a skill
and execute each block in an isolated subprocess with a timeout, reporting the
result per block. A block annotated with `# qskill: skip` SHALL be reported as
skipped and SHALL NOT fail the run.

#### Scenario: A snippet that raises fails the run
- **WHEN** a skill contains a Python block that raises an exception, or exceeds
  the timeout
- **THEN** the runner reports the file, the block order and the captured error,
  and exits non-zero

#### Scenario: A required-credentials snippet is skipped
- **WHEN** a block is annotated with `# qskill: skip`
- **THEN** the runner lists it as skipped and the run can still exit 0

#### Scenario: All snippets execute
- **WHEN** every Python block in a skill runs successfully
- **THEN** the runner exits 0 and prints how many blocks passed

### Requirement: Skill scaffolding

`scripts/new_skill.py <skill-id>` SHALL create `.agents/skills/<skill-id>/` from
the canonical template with a `SKILL.md`, a `references/api-map.md` stub and a
`scripts/check_env.py` stub, and SHALL refuse to overwrite an existing skill.

#### Scenario: Scaffolding a new skill
- **WHEN** a contributor runs `python scripts/new_skill.py demo` and no `demo`
  skill exists
- **THEN** the template files are created and the generated skill passes the
  linter

#### Scenario: Existing skill is protected
- **WHEN** the target skill directory already exists
- **THEN** the script reports the conflict, makes no change and exits non-zero

### Requirement: Eval case execution

`evals/run.py` SHALL discover YAML eval cases under `evals/cases/<skill-id>/`,
SHALL support listing them without executing anything, and SHALL report a pass
or fail result per case. Supported checks SHALL include `required_patterns`,
`forbidden_patterns`, `snippet_runs` and `numeric_close`.

#### Scenario: Listing with no cases
- **WHEN** `evals/cases/` contains no case files and the runner is invoked with
  `--list`
- **THEN** it exits 0 and reports that zero cases were found

#### Scenario: A failing check fails the case
- **WHEN** a case's `forbidden_patterns` matches the produced answer, or a
  `numeric_close` check is outside its tolerance
- **THEN** the runner reports the case id and the failed check, and exits
  non-zero

#### Scenario: No network access required
- **WHEN** the eval suite runs on a machine without credentials or internet
- **THEN** every case still produces a deterministic result

### Requirement: Reproducible environment

The repository SHALL declare Python 3.12 and pinned dependency extras for Qiskit,
PennyLane, Cirq and development tooling, and the linter SHALL run using only the
development tooling, without requiring any quantum SDK to be installed.

#### Scenario: Linting without quantum SDKs
- **WHEN** only the development tooling is installed
- **THEN** `scripts/skill_lint.py` completes and reports its result

#### Scenario: Pinned versions are discoverable
- **WHEN** a contributor reads `pyproject.toml`
- **THEN** each supported SDK is available as a named extra with an explicit
  version constraint
