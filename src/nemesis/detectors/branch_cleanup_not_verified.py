"""Detector for the ``branch_cleanup_not_verified`` failure mode.

The failure: branches were merged but not always deleted or confirmed clean,
so merged branches lingered after a phase closed.

Detection rule: a branch was merged but not deleted.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "branch_cleanup_not_verified"


@register_detector
@dataclass(frozen=True)
class BranchCleanupNotVerifiedDetector:
    """Detects a branch that was merged but never deleted."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if a branch was merged but not deleted."""
        evidence: list[str] = []

        branch_merged = artifact.repo_state.get("branch_merged")
        branch_deleted = artifact.repo_state.get("branch_deleted")

        if branch_merged and not branch_deleted:
            evidence.append(
                "branch_merged=True but branch_deleted=False — "
                "merged branch was never cleaned up"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id,
                detected=True,
                evidence=evidence,
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id,
            detected=False,
            evidence=[],
        )
