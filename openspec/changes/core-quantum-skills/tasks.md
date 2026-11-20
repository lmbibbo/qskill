# Tasks

## 1. Environment and scaffolding

- [ ] 1.1 Sync the pinned environment with `uv sync --all-extras` and verify `uv run python -c "import qiskit, qiskit_aer, yaml; print(qiskit.__version__)"` prints a 2.4.x version.
- [ ] 1.2 Scaffold the three skills with `uv run python scripts/new_skill.py qiskit-workflow`, `... quantum-validation` and `... quantum-project`; verify each directory contains `SKILL.md`, `references/api-map.md` and `scripts/check_env.py`, and that `uv run python scripts/skill_lint.py .agents/skills/qiskit-workflow .agents/skills/quantum-validation .agents/skills/quantum-project` exits 0.

## 2. qiskit-workflow (framework skill)

- [ ] 2.1 Write `.agents/skills/qiskit-workflow/references/api-map.md` covering Qiskit 2.4 imports, `QuantumCircuit`, `SamplerV2`/`StatevectorSampler`, `EstimatorV2`, `transpile`, `generate_preset_pass_manager` and `qiskit_aer`; verify no 1.x-only symbol (`execute(`, `BasicAer`, `qiskit.execute`) appears and that every listed import resolves with `uv run python -c "import qiskit, qiskit_aer"`.
- [ ] 2.2 Write `references/patterns.md` with Bell, GHZ, measurement and parametrized-circuit patterns; verify each pattern has a corresponding snippet or eval case in the skill and that the eval case ids referenced from the file exist.
- [ ] 2.3 Write `references/migration-1x-2x.md` listing each removed 1.x API and its 2.x replacement; verify every removed API named there appears in a `forbidden_patterns` check of `evals/cases/qiskit-workflow/reject-old-api.yaml`.
- [ ] 2.4 Write `SKILL.md` (workflow `build -> transpile -> execute -> measure`, pitfalls, links to the three references, the description from design.md) and verify it stays at or below 500 lines with `wc -l` and that `uv run python scripts/skill_lint.py .agents/skills/qiskit-workflow` reports 0 errors and 0 warnings.
- [ ] 2.5 Verify every Python block in `SKILL.md` executes: `uv run python scripts/run_snippets.py .agents/skills/qiskit-workflow` reports 0 failed blocks.
- [ ] 2.6 Write `scripts/check_env.py` (Python 3.12, Qiskit version range, critical imports, actionable install message); verify it exits 0 under `uv run` and non-zero under the system `python3` without Qiskit, printing `uv sync --extra qiskit`.
- [ ] 2.7 Write eval cases `evals/cases/qiskit-workflow/{bell-state,transpile-line,sampler-v2,reject-old-api}.yaml` with the checks from design.md decision 4; verify `uv run python evals/run.py --cases evals/cases/qiskit-workflow` exits 0 with 4/4 passed.
- [ ] 2.8 Run the skill validation gate: lint, snippets and the four eval cases for `qiskit-workflow` all green in one command sequence, with the pass counts recorded.

## 3. quantum-validation (stage skill)

- [ ] 3.1 Write `references/simulation-modes.md` explaining statevector, shot-based and density-matrix simulation and when each is the right check; verify the decision table names the mode used by each validation eval case.
- [ ] 3.2 Write `references/testing.md` covering explicit seeds, deterministic reruns, tolerance selection and snapshot-style assertions; verify every seed rule is exercised by `evals/cases/quantum-validation/seed-reproducibility.yaml`.
- [ ] 3.3 Write `references/statistics.md` covering standard error, confidence intervals and the shot-count formula; verify the worked examples reproduce the tolerance used in `evals/cases/quantum-validation/bell-distribution.yaml`.
- [ ] 3.4 Write `SKILL.md` with the description from design.md, the validate-before-reporting workflow and links to the three references; keep it framework-neutral (no SDK imports) and verify `uv run python scripts/skill_lint.py .agents/skills/quantum-validation` reports 0 errors and 0 warnings.
- [ ] 3.5 Verify any Python block in `SKILL.md` is framework-neutral and executes: `uv run python scripts/run_snippets.py .agents/skills/quantum-validation` reports 0 failed blocks.
- [ ] 3.6 Write `scripts/check_env.py` reporting Python 3.12 and which optional SDK extras are installed, without requiring one; verify it exits 0 in the pinned environment and prints a remediation line when an extra is absent.
- [ ] 3.7 Write eval cases `evals/cases/quantum-validation/{bell-distribution,ghz-state,seed-reproducibility}.yaml` with framework-neutral recorded snippets and the checks from design.md decision 4; verify `uv run python evals/run.py --cases evals/cases/quantum-validation` exits 0 with 3/3 passed.
- [ ] 3.8 Run the skill validation gate: lint, snippets and the three eval cases for `quantum-validation` all green in one command sequence, with the pass counts recorded.

## 4. quantum-project (hub skill)

- [ ] 4.1 Write `references/lifecycle.md` with the stage-by-stage lifecycle and the hand-off point to each skill; verify every skill it names exists under `.agents/skills/`.
- [ ] 4.2 Write `references/framework-choice.md` with the Qiskit/PennyLane/Cirq matrix, marking Qiskit as the stage 1 choice and the other two as deferred; verify the deferral matches `docs/roadmap.md` stage 3.
- [ ] 4.3 Write `references/project-shapes.md` with the circuit, variational and optimization shapes, the skeleton and success metric of each, and the deferral of algorithm detail to stage 2; verify all three shapes are present, the variational entry names an ansatz/Hamiltonian/optimizer and the QUBO entry names a model/mapping/solver, and no algorithm implementation appears in the file.
- [ ] 4.4 Write `references/project-layout.md` with the invariant core shared by all shapes (pinned environment, `src/`/`tests/`/`scripts/`, seeds, validation hand-off) and the version policy; verify each of the three skeletons in `project-shapes.md` reuses that core and the layout matches the commands in `README.md` (`uv sync`, `uv run python`).
- [ ] 4.5 Write `SKILL.md` with the description from design.md, a decision tree that classifies the deliverable before the skill, the delegation table and links to the four references; verify `uv run python scripts/skill_lint.py .agents/skills/quantum-project` reports 0 errors and 0 warnings.
- [ ] 4.6 Write `scripts/check_env.py` reporting Python 3.12 and the optional SDK extras; verify it exits 0 in the pinned environment and exits non-zero below Python 3.12.
- [ ] 4.7 Verify the hub introduces neither framework syntax nor algorithm implementation: `grep -E "QuantumCircuit|SamplerV2|qiskit" .agents/skills/quantum-project/SKILL.md` returns no code-level API usage beyond the skill name and links, and `uv run python scripts/run_snippets.py .agents/skills/quantum-project` reports 0 failed blocks.
- [ ] 4.8 Write `evals/cases/quantum-project/vqe-shape.yaml` with the `Loaded skills:` trace, variational vocabulary and forbidden Qiskit API patterns; verify `uv run python evals/run.py --cases evals/cases/quantum-project` exits 0 with 1/1 passed.
- [ ] 4.9 Run the skill validation gate: lint, snippets and the one project-shape eval for `quantum-project` all green in one command sequence, with the pass counts recorded.

## 5. Routing evals and description calibration

- [ ] 5.1 Add `evals/cases/routing/{qiskit-task,validation-task,ambiguous-task}.yaml` using the `Loaded skills:` trace convention from design.md decision 3, each paired with a content assertion; verify `uv run python evals/run.py --list` shows all eleven stage 1 cases with no duplicate ids.
- [ ] 5.2 Run `uv run python evals/run.py --cases evals/cases/routing`; if any case fails, tune the three `description` values and rerun until 3/3 pass, then confirm `uv run python scripts/skill_lint.py .agents/skills/quantum-project .agents/skills/qiskit-workflow .agents/skills/quantum-validation` still reports no trigger-collision warnings.
- [ ] 5.3 Run the full stage 1 suite with `uv run python evals/run.py`; verify the pass rate is at least 9/11, all three routing cases pass, and the failing cases (if any) are documented with the reason they are accepted.

## 6. Documentation and stage close

- [ ] 6.1 Update `README.md` status and skill list so the three new skills appear with their triggers; verify every command quoted in the README runs as written.
- [ ] 6.2 Update `docs/roadmap.md` stage 1 status line with the close date and the measured eval pass rate; verify the file no longer says stage 1 is pending.
- [ ] 6.3 Reproduce the acceptance criteria from a clean environment: `rm -rf .venv && uv sync --all-extras`, then lint, snippets and the full eval suite; verify 0 lint warnings, 0 failed snippets and the recorded pass rate, and record the numbers in `docs/roadmap.md`.
- [ ] 6.4 Manual read-through of the three `SKILL.md` files by a human, following the lifecycle from the hub to the other two; record the reviewer and the date in `docs/roadmap.md`.
- [ ] 6.5 Run `openspec validate core-quantum-skills --strict` and verify it passes with no warnings.

## Workflow follow-up

- Archive the change with the archive workflow once the stage acceptance criteria and the human read-through are recorded.
- Confirm `openspec/specs/` contains `skill-routing`, `framework-qiskit`,
  `circuit-validation` and `project-structure` after archiving.
