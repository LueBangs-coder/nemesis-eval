"""Detector for the ``testing_without_source_verification`` failure mode.

The failure: tests passed in the wrong folder or on a stale branch because the
source was never verified before accepting the results.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "testing_without_source_verification"


@register_detector
@dataclass(frozen=True)
class TestingWithoutSourceVerificationDetector:
    """Detects test results accepted without source verification."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if tests were run without verifying the source first."""
        evidence: list[str] = []

        if artifact.repo_state.get("source_verified") is False:
            tested_branch = artifact.repo_state.get("tested_branch")
            evidence.append(
                "source_verified=False — test results accepted without confirming "
                f"the source (tested_branch={tested_branch!r})"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
