# Contributing to Nemesis

Thanks for your interest. Nemesis is a focused research artifact, so
contributions stay close to its purpose: turning documented agentic failure
modes into programmatic detectors with empirical grounding.

## Ground rules

- **Every detector traces to a real failure mode.** New detectors must target
  a mode in [`data/failure_modes.yaml`](./data/failure_modes.yaml). If you want
  to add a mode, open an issue first to discuss the empirical grounding.
- **Tests are required.** Every detector ships with tests covering at least one
  positive case (failure present) and the clean-run negative case.
- **The gates are non-negotiable.** `pytest` and `pre-commit run --all-files`
  must both pass before a PR is considered.

## Development setup

```bash
git clone https://github.com/LueBangs-coder/nemesis-eval.git
cd nemesis-eval
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pre-commit install
pytest
```

## Adding a detector

1. Create `src/nemesis/detectors/<failure_mode_id>.py`.
2. Define a frozen dataclass detector decorated with `@register_detector` and
   `@dataclass(frozen=True)`. Set `failure_mode_id` to the mode it targets.
   Implement `detect(self, artifact) -> DetectionResult`.
3. Add the module to the imports in `src/nemesis/detectors/__init__.py` so it
   registers when the package loads.
4. Add a synthetic signature for the mode in `src/nemesis/test_agent.py` if one
   does not already exist, so the eval loop can generate a known-truth run.
5. Add tests under `tests/detectors/`.
6. Run `pytest` and `pre-commit run --all-files`.

## Pull requests

- One concern per PR. Keep changes small and reviewable.
- Use conventional commit prefixes (`feat:`, `fix:`, `docs:`, `test:`,
  `refactor:`, `chore:`).
- Describe what the change does and how you verified it.

## Reporting issues

Issues are welcome any time. For a detector that misfires, include the
`RunArtifact` inputs and the observed vs. expected `DetectionResult`.
