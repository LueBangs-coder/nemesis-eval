"""Detector for the ``skill_bloat`` failure mode.

The failure: agent skills became too large, too project-specific, or
overloaded, losing portability.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "skill_bloat"


@register_detector
@dataclass(frozen=True)
class SkillBloatDetector:
    """Detects a skill that has grown non-portable."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if a skill is no longer portable."""
        evidence: list[str] = []

        if artifact.repo_state.get("skill_is_portable") is False:
            line_count = artifact.repo_state.get("skill_line_count")
            evidence.append(
                "skill_is_portable=False — skill has bloated "
                f"(skill_line_count={line_count}); not small/portable/composable"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
