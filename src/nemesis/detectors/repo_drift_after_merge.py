"""Detector for the ``repo_drift_after_merge`` failure mode.

The failure: a PR was merged remotely while the local project folder stayed
behind, so local and remote drifted out of parity.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "repo_drift_after_merge"


@register_detector
@dataclass(frozen=True)
class RepoDriftAfterMergeDetector:
    """Detects local/remote drift after a merge."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if local parity with remote was not confirmed after merge."""
        evidence: list[str] = []

        if artifact.repo_state.get("local_parity") is False:
            evidence.append(
                "local_parity=False — remote merged but local checkout was not "
                "brought to parity"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
