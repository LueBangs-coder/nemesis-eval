"""Detector for the ``missing_root_doctrine_updates`` failure mode.

The failure: behavior changed but root doctrine files (CLAUDE.md, AGENTS.md,
WORKLOG.md, etc.) were not updated.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "missing_root_doctrine_updates"


@register_detector
@dataclass(frozen=True)
class MissingRootDoctrineUpdatesDetector:
    """Detects changed behavior without root doctrine updates."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if behavior changed but root docs were not updated."""
        evidence: list[str] = []

        behavior_changed = artifact.repo_state.get("behavior_changed")
        root_docs_updated = artifact.repo_state.get("root_docs_updated")

        if behavior_changed and not root_docs_updated:
            evidence.append(
                "behavior_changed=True but root_docs_updated=False — doctrine "
                "files were not updated to match the behavior change"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
