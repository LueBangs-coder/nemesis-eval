"""Tests for the SyntheticAgent and its failure-injection signatures."""

from pathlib import Path

import pytest

from nemesis.catalog import load_catalog
from nemesis.detectors.declared_success_too_early import (
    DeclaredSuccessTooEarlyDetector,
)
from nemesis.test_agent import SIGNATURES, SyntheticAgent, Task, manifests

CATALOG_PATH = Path(__file__).parent.parent / "data" / "failure_modes.yaml"


@pytest.fixture
def agent() -> SyntheticAgent:
    """A fresh synthetic agent for each test."""
    return SyntheticAgent()


@pytest.fixture
def task() -> Task:
    """A simple synthetic task."""
    return Task(name="demo", description="a demo task")


@pytest.fixture
def catalog_ids() -> list[str]:
    """All failure-mode ids from the catalog."""
    return [mode.id for mode in load_catalog(CATALOG_PATH)]


def test_signatures_cover_every_catalog_mode(catalog_ids: list[str]) -> None:
    """There must be exactly one injection signature per catalog mode."""
    assert set(SIGNATURES.keys()) == set(catalog_ids)


def test_clean_run_injects_nothing(agent: SyntheticAgent, task: Task) -> None:
    """A run with no injections must not exhibit any failure."""
    artifact = agent.run(task, inject=[])
    assert artifact.claimed_success is False
    for mode_id in SIGNATURES:
        assert not manifests(artifact, mode_id)


def test_run_none_inject_is_clean(agent: SyntheticAgent, task: Task) -> None:
    """run() with inject=None behaves like an empty injection list."""
    artifact = agent.run(task)
    assert artifact.claimed_success is False


@pytest.mark.parametrize("mode_id", sorted(SIGNATURES.keys()))
def test_every_mode_can_be_injected(
    agent: SyntheticAgent, task: Task, mode_id: str
) -> None:
    """For every mode, run(inject=[mode]) yields an artifact exhibiting it."""
    artifact = agent.run(task, inject=[mode_id])
    assert manifests(artifact, mode_id), f"{mode_id} was not exhibited after injection"


def test_injected_failure_is_caught_by_real_detector(
    agent: SyntheticAgent, task: Task
) -> None:
    """Cross-validation: the Phase 2 detector fires on the injected failure."""
    artifact = agent.run(task, inject=["agent_declared_success_too_early"])
    detector = DeclaredSuccessTooEarlyDetector()
    result = detector.detect(artifact)
    assert result.detected is True
    assert result.evidence  # non-empty evidence on a positive detection


def test_clean_run_is_not_caught_by_real_detector(
    agent: SyntheticAgent, task: Task
) -> None:
    """Cross-validation: the Phase 2 detector does NOT fire on a clean run."""
    artifact = agent.run(task, inject=[])
    detector = DeclaredSuccessTooEarlyDetector()
    result = detector.detect(artifact)
    assert result.detected is False


def test_multiple_injections_compose(agent: SyntheticAgent, task: Task) -> None:
    """Injecting two modes yields an artifact exhibiting both."""
    artifact = agent.run(
        task,
        inject=["dirty_worktree_after_closeout", "branch_cleanup_not_verified"],
    )
    assert manifests(artifact, "dirty_worktree_after_closeout")
    assert manifests(artifact, "branch_cleanup_not_verified")


def test_unknown_mode_raises(agent: SyntheticAgent, task: Task) -> None:
    """Injecting an unregistered mode id raises KeyError."""
    with pytest.raises(KeyError, match="no failure signature"):
        agent.run(task, inject=["not_a_real_mode"])


def test_supported_modes_matches_signatures(agent: SyntheticAgent) -> None:
    """supported_modes reports exactly the registered signature ids."""
    assert set(agent.supported_modes) == set(SIGNATURES.keys())
