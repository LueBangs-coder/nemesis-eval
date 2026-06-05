# CLAUDE.md — Nemesis

Operating contract for Claude Code working in the Nemesis repo.

**Project:** Nemesis — Python evaluation harness for agentic failure modes.
**Reference spec:** `BUILD_SPEC.md` (full phase-by-phase plan).
**Author:** Luis A. Betancourt — Founder & Operator, Onslaught Gaming LLC.
**Status:** Pre-alpha. Phase 0 in flight.
**Parent project:** Pantheon (private operating context; public architectural writeup available on request).

---

## Read first, every session

Before any change to the repo:

1. Read this file completely.
2. Read `BUILD_SPEC.md` if not already loaded.
3. Identify the current phase under `## Current Phase` below.
4. Operate within that phase only — do not skip ahead.
5. Treat the current phase's **acceptance gate** as the stop condition.

---

## Doctrine

Same family as Pantheon. These rules govern every change.

- **Named contracts over implicit behavior.** Every module, function, and test has a name and a documented contract.
- **Fail-closed when in doubt.** If a check is ambiguous, default to "not done."
- **Bounded responsibility per module.** No module does more than one thing.
- **Documented capability surface.** `README.md` is the canonical statement of what Nemesis does. Do not let behavior outpace documentation.
- **Empirical grounding.** Every detector traces back to a real production failure in `data/failure_modes.yaml`.
- **Teach, don't just build.** Luis is using this project to learn Python end-to-end. Explain concepts as they're introduced.
- **NEW BUILD — do not patch.** If a phase's spec materially changes, restart the phase. Do not patch around outdated structure.

---

## Operating rules

When working on Nemesis, you must:

1. **Stay in the current phase.** Do not skip ahead.
2. **Use the phase's acceptance gate as the stop condition.** A phase completes only when its gate passes verifiably.
3. **Teach before you build.** For each new Python concept, briefly explain what it is, why it's the right tool, and where to learn more. Then write the code.
4. **Honor declared learning checkpoints.** When a phase declares a checkpoint, pause and ask Luis to write the code himself. Review afterward.
5. **Run tests after every meaningful change.** `pytest` must exit 0 before the change is considered complete.
6. **Lint and format before commit.** `pre-commit run --all-files` must pass. No commits with failing linters.
7. **Verify the actual repo state.** Before declaring success: branch, HEAD, upstream parity, worktree status, and test results. Per Pantheon's first-principle failure (`agent_declared_success_too_early`), your own transcript is not proof. The checkout is.
8. **Use complete handoff prompts.** When closing a phase or handing off, the final report must include: branch, HEAD, upstream status, worktree status, and the names of new files added.

---

## Stop conditions

Stop and ask Luis before:

- Adding paid APIs or services
- Adding cloud deployment
- Adding browser automation
- Skipping the current phase's acceptance gate
- Expanding scope beyond the current phase
- Storing any production data (this harness operates only on synthetic test agents)
- Changing the project's public-facing claims (the README)
- Modifying the failure-mode catalog without explicit approval
- Flipping the repo to public visibility (Phase 5 gate only)

---

## Current Phase

### Phase 5 — Reporting, artifact, public release — CODE COMPLETE; release gates pending

The code and documentation deliverables are merged-pending on branch
`phase-5-reporting-release`. Two release actions remain, each a hard
stop-condition requiring explicit Luis approval:

1. **Tag `v0.1.0`** on GitHub with release notes linking the Pantheon writeup.
2. **Flip the repo to public** at `github.com/LueBangs-coder/nemesis`.

Until both are done by explicit approval, the project is feature-complete but
private. Do not flip visibility or tag a release without per-operation
authorization.

**Acceptance gate — verified portions:**
- `nemesis eval --output report.md` produces a structured Markdown report
  (per-mode TPR/FPR, evidence, Pantheon link). ✅
- Fresh-clone install + run works end to end without manual fixes (verified in
  a temp clone: fresh venv, `pip install -e ".[dev]"`, 59 tests pass, CLI runs). ✅
- `pytest` → 59 passed. ✅
- `pre-commit run --all-files` → ruff + black Passed. ✅

**Acceptance gate — pending release approval:**
- Repo public at `github.com/LueBangs-coder/nemesis`. ⏳
- README renders on the GitHub web view (verify after public). ⏳
- `v0.1.0` tagged; release notes link the Pantheon writeup. ⏳

---

## Closed phases

### Phase 4 — Eval loop and remaining detectors — CLOSED

Closed on 2026-05-27. Acceptance gate verified (and overdelivered):
- All 20 modes have detectors (gate required ≥15) — one detector per file in `src/nemesis/detectors/`
- `python -m nemesis eval` runs all 20 detectors against `SyntheticAgent` output and prints structured results with evidence
- True-positive rate 1.00 for every detector; false-positive rate 0.00 for every detector (negative trials = clean run + every other mode's injection)
- `pytest` → `53 passed`
- `pre-commit run --all-files` → ruff Passed, black Passed

Files delivered: 16 new detectors + the registry machinery in `detectors/base.py` (`register_detector`, `all_detectors`), `detectors/__init__.py` (auto-import wiring so all detectors register), `src/nemesis/eval.py` (`EvalLoop`, `DetectorScore`, `EvalReport`), `src/nemesis/__main__.py` (the `python -m nemesis eval` CLI via argparse + logging), `tests/test_eval.py`. Learning checkpoint completed — Luis hand-wrote two detectors (`branch_cleanup_not_verified`, `dirty_worktree_after_closeout`) from scratch after a worked example; both correct on first pass (only cosmetic cleanup). Concepts: registry pattern with decorators, decorator stacking order, logging module, `python -m`/`__main__.py`, confusion-matrix metrics (TPR/FPR).

### Phase 3 — Synthetic test agent — CLOSED

Closed on 2026-05-27. Acceptance gate verified:
- For every catalog mode (all 20), `SyntheticAgent.run(inject=[mode_id])` produces a `RunArtifact` exhibiting that failure (20 parameterized tests pass)
- Cross-validation bonus: the Phase 2 detector fires on the injected `agent_declared_success_too_early` artifact and stays silent on clean runs
- `pytest` → `44 passed in 0.25s`
- `pre-commit run --all-files` → ruff Passed, black Passed

Files delivered: `src/nemesis/test_agent.py` (`Task`, `FailureSignature`, `SyntheticAgent`, `manifests`, data-driven `SIGNATURES` registry — Strategy pattern, one signature per mode), `tests/test_agent.py` (signature/catalog parity, per-mode injection, clean-run, composition, cross-validation, error path). Implemented with composition over inheritance and frozen-dataclass immutability (`dataclasses.replace`).

### Phase 2 — One detector, end to end — CLOSED

Closed on 2026-05-27. Acceptance gate verified:
- `DeclaredSuccessTooEarlyDetector.detect(artifact)` returns `DetectionResult(failure_mode_id, detected, evidence)`
- 3 positive parameterized cases + 3 negative parameterized cases + 2 shape tests pass
- `pytest` → `16 passed in 0.61s`
- `pre-commit run --all-files` → ruff Passed, black Passed

Files delivered: `src/nemesis/detectors/__init__.py`, `src/nemesis/detectors/base.py` (`RunArtifact`, `DetectionResult`, `Detector` Protocol), `src/nemesis/detectors/declared_success_too_early.py` (first real detector), `tests/detectors/__init__.py`, `tests/detectors/test_declared_success_too_early.py`. Learning checkpoint completed — Luis designed the `DetectionResult` shape on paper before seeing the proposal; final shape adopted `failure_mode_id`, `detected`, `evidence` after discussion of why evidence is the most important field.

### Phase 1 — Failure mode data model — CLOSED

Closed on 2026-05-27. Acceptance gate verified:
- `load_catalog()` returns exactly 20 `FailureMode` objects (8 verification + 5 state_hygiene + 3 doctrine + 2 scope + 2 skill_design)
- Each mode has `id`, `name`, `category` (Category enum), `description`, `fix_rule`
- `pytest` → `8 passed in 0.76s` (1 smoke + 7 catalog)
- `pre-commit run --all-files` → ruff Passed, black Passed

Files delivered: `src/nemesis/models.py` (FailureMode + Category + Severity), `src/nemesis/catalog.py` (`load_catalog` with structural validation), `data/failure_modes.yaml` (the 20-mode catalog), `tests/test_catalog.py` (count, fields, types, uniqueness, error paths). `PyYAML>=6.0` added as runtime dependency. Learning checkpoint completed — Luis hand-typed `models.py` with concept-by-concept explanation (type hints, dataclasses, enums, pathlib, PyYAML).

### Phase 0 — Environment, scaffolding, and repo — CLOSED

Closed on 2026-05-27. Acceptance gate verified:
- `pip install -e ".[dev]"` succeeded (Python 3.13.6, hatchling backend)
- `pytest` → `1 passed in 0.07s`
- `pre-commit run --all-files` → ruff Passed, black Passed
- README links to `BUILD_SPEC.md`

Files delivered: `pyproject.toml`, `src/nemesis/__init__.py`, `tests/test_smoke.py`, `LICENSE` (MIT), `.gitignore`, `.pre-commit-config.yaml`. Learning checkpoint completed — Luis hand-typed `pyproject.toml` with field-by-field explanation.

---

## When the phase passes

1. Update `## Current Phase` in this file to the next phase from `BUILD_SPEC.md`.
2. Commit the doctrine change: `docs: advance to Phase N`.
3. Begin the next phase under the same rules.
4. Do not patch backward into prior phases. The phase that passed is closed.

---

## Repo conventions

- **Branches:** feature-branches-per-phase. Each phase's work lives on a branch named `phase-N-shortname` (e.g., `phase-2-detector`). Merge to `main` only via PR after the phase's acceptance gate passes. `main` is protected and always green. The branch is deleted (local and remote) after merge.
- **Commits:** conventional prefixes (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).
- **Tests:** every new module ships with a test file under `tests/` mirroring the module path.
- **Type hints:** required on every public function signature.
- **Docstrings:** required on every public function and class. One-line summary minimum.

---

## Communication

If Claude Code encounters anything that requires Luis's input — ambiguity in a spec, a stop condition triggered, a learning checkpoint, an unverifiable claim — pause and ask. Do not assume. Do not patch silently. Do not declare success early.

---

*Built in the Pantheon's shadow.*
