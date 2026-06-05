# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - Unreleased

### Added
- **Real-repository adapter** (`nemesis check`): runs the detectors against a
  real repository, building the run artifact from read-only git state
  (worktree status, branch, HEAD, upstream parity). Nemesis never executes the
  target project's code or tests — test outcomes are passed in.
- **`--fail-on-detect`** flag on `nemesis check`: exit non-zero when any
  failure mode fires, so the check can gate CI. Default stays report-only.
- **GitHub Action** (`action.yml`): a composite action wrapping `nemesis check`
  so any repository can run a check in its workflow.
- **Tokenless PyPI release pipeline** (`.github/workflows/release.yml`):
  publishes on a GitHub Release via Trusted Publishing (OIDC) — no API token
  and no repository secret.
- `py.typed` marker (PEP 561): the package ships its inline type hints.

### Changed
- **Distribution renamed to `nemesis-eval`** (the PyPI name `nemesis` was
  already taken). The import package and CLI remain `nemesis`.
- `pyproject.toml`: added keywords, trove classifiers, project URLs, and an
  explicit wheel package mapping so the build is correct under the new name.

## [0.1.0] - 2026-06-05

### Added
- Initial public release: 20 detectors for agentic failure modes grounded in a
  documented failure-mode catalog.
- `nemesis eval`: scores every detector against synthetic known-truth runs and
  renders a Markdown report (`--output`).

[Unreleased]: https://github.com/LueBangs-coder/nemesis-eval/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/LueBangs-coder/nemesis-eval/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/LueBangs-coder/nemesis-eval/releases/tag/v0.1.0
