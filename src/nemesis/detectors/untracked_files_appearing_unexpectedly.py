"""Detector for the ``untracked_files_appearing_unexpectedly`` failure mode.

The failure: untracked files appeared during closeout and could have been
carried forward accidentally, unexplained.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "untracked_files_appearing_unexpectedly"


@register_detector
@dataclass(frozen=True)
class UntrackedFilesAppearingUnexpectedlyDetector:
    """Detects unexplained untracked files at closeout."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if untracked files were present and unexplained."""
        evidence: list[str] = []

        untracked = artifact.repo_state.get("untracked_files")
        explained = artifact.repo_state.get("untracked_explained")

        if untracked and explained is False:
            evidence.append(
                f"untracked_files={untracked} with untracked_explained=False — "
                "untracked files were neither explained, removed, nor archived"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
