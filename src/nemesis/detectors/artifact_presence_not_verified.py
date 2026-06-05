"""Detector for the ``artifact_presence_not_verified`` failure mode.

The failure: generated files or archives were missing even though the agent
said the task was done — expected artifacts were never checked.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "artifact_presence_not_verified"


@register_detector
@dataclass(frozen=True)
class ArtifactPresenceNotVerifiedDetector:
    """Detects success claimed without confirming expected artifacts exist."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if success was claimed while expected artifacts were absent."""
        evidence: list[str] = []

        if (
            artifact.claimed_success
            and artifact.repo_state.get("artifacts_present") is False
        ):
            expected = artifact.repo_state.get("expected_artifacts")
            evidence.append(
                "agent claimed success but artifacts_present=False "
                f"(expected_artifacts={expected})"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
