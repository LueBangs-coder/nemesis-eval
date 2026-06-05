"""Detector for the ``hot_file_conflict_risk`` failure mode.

The failure: multiple agents or sessions could touch root doctrine files
without coordination.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "hot_file_conflict_risk"


@register_detector
@dataclass(frozen=True)
class HotFileConflictRiskDetector:
    """Detects a hot file touched without a coordination gate."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if a hot file was edited without coordination."""
        evidence: list[str] = []

        hot_file = artifact.repo_state.get("hot_file_touched")
        coordination_gate = artifact.repo_state.get("coordination_gate")

        if hot_file and coordination_gate is False:
            evidence.append(
                f"hot_file_touched={hot_file!r} with coordination_gate=False — "
                "a doctrine hot file was edited without a coordination gate"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
