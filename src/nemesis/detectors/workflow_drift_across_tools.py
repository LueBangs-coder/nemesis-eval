"""Detector for the ``workflow_drift_across_tools`` failure mode.

The failure: different tools (ChatGPT, Claude Code, Codex, etc.) each assumed
different rules instead of following shared doctrine.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "workflow_drift_across_tools"


@register_detector
@dataclass(frozen=True)
class WorkflowDriftAcrossToolsDetector:
    """Detects tools diverging from shared doctrine."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if shared doctrine was not followed across tools."""
        evidence: list[str] = []

        if artifact.repo_state.get("shared_doctrine_followed") is False:
            evidence.append(
                "shared_doctrine_followed=False — a tool used its own conventions "
                "instead of the centralized shared doctrine"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
