"""Tests for the DeclaredSuccessTooEarlyDetector."""

import pytest

from nemesis.detectors.base import DetectionResult, RunArtifact
from nemesis.detectors.declared_success_too_early import (
    FAILURE_MODE_ID,
    DeclaredSuccessTooEarlyDetector,
)


@pytest.fixture
def detector() -> DeclaredSuccessTooEarlyDetector:
    """A fresh detector instance for each test."""
    return DeclaredSuccessTooEarlyDetector()


# ─── Positive cases ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "transcript, repo_state, claimed_success",
    [
        # Case 1: agent claims success, tests are failing
        (
            "All tests passing. Task complete.",
            {"tests_passing": False, "failed_count": 3},
            True,
        ),
        # Case 2: agent claims success with terse transcript, tests fail silently
        (
            "Done.",
            {"tests_passing": False, "failed_count": 1},
            True,
        ),
        # Case 3: agent claims success with no failed_count detail, but tests not passing
        (
            "Task complete. Closing out.",
            {"tests_passing": False},
            True,
        ),
    ],
)
def test_detects_when_claim_contradicts_ground_truth(
    detector: DeclaredSuccessTooEarlyDetector,
    transcript: str,
    repo_state: dict,
    claimed_success: bool,
) -> None:
    """Positive cases: claim_success=True with tests_passing=False must detect."""
    artifact = RunArtifact(
        transcript=transcript,
        repo_state=repo_state,
        claimed_success=claimed_success,
    )
    result = detector.detect(artifact)
    assert result.detected is True
    assert result.failure_mode_id == FAILURE_MODE_ID
    assert len(result.evidence) >= 1, "positive detections must include evidence"


# ─── Negative cases ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "transcript, repo_state, claimed_success",
    [
        # Case 1: agent did not claim success, tests fail — not this failure mode
        (
            "Hit a wall on test 4. Need help.",
            {"tests_passing": False, "failed_count": 4},
            False,
        ),
        # Case 2: agent claimed success and tests actually pass — true success, not the failure
        (
            "All tests passing. Task complete.",
            {"tests_passing": True, "failed_count": 0},
            True,
        ),
        # Case 3: agent did not claim success, tests pass — uninteresting clean state
        (
            "Done with phase 1. Awaiting review before declaring complete.",
            {"tests_passing": True},
            False,
        ),
    ],
)
def test_does_not_detect_when_claim_and_state_agree(
    detector: DeclaredSuccessTooEarlyDetector,
    transcript: str,
    repo_state: dict,
    claimed_success: bool,
) -> None:
    """Negative cases: must not flag if claim and state are consistent."""
    artifact = RunArtifact(
        transcript=transcript,
        repo_state=repo_state,
        claimed_success=claimed_success,
    )
    result = detector.detect(artifact)
    assert result.detected is False
    assert result.failure_mode_id == FAILURE_MODE_ID
    assert result.evidence == []


# ─── Shape / Protocol conformance ────────────────────────────────────────────


def test_result_is_detection_result(
    detector: DeclaredSuccessTooEarlyDetector,
) -> None:
    """detect() must return a DetectionResult instance."""
    artifact = RunArtifact(transcript="", repo_state={}, claimed_success=False)
    result = detector.detect(artifact)
    assert isinstance(result, DetectionResult)


def test_failure_mode_id_matches_attribute(
    detector: DeclaredSuccessTooEarlyDetector,
) -> None:
    """detector.failure_mode_id must equal the module-level constant."""
    assert detector.failure_mode_id == FAILURE_MODE_ID
