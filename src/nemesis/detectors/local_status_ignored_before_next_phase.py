"""Detector for the ``local_status_ignored_before_next_phase`` failure mode.

The failure: a new phase started before confirming the previous phase was
truly closed.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "local_status_ignored_before_next_phase"


@register_detector
@dataclass(frozen=True)
class LocalStatusIgnoredBeforeNextPhaseDetector:
    """Detects a new phase begun before closeout checks ran."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if the previous phase was not confirmed closed."""
        evidence: list[str] = []

        if artifact.repo_state.get("previous_phase_closed") is False:
            evidence.append(
                "previous_phase_closed=False — next phase started without "
                "confirming the prior phase's closeout"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
