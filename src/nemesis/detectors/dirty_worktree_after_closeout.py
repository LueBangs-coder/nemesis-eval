"""Detector for the ``dirty_worktree_after_closeout`` failure mode.

The failure: modified and untracked files remained after the agent claimed
the phase was complete.

Detection rule: the agent claimed success while the worktree was not clean.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "dirty_worktree_after_closeout"


@register_detector
@dataclass(frozen=True)
class DirtyWorktreeAfterCloseoutDetector:
    """Detects success claimed while the worktree was left dirty."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if the worktree was left dirty after closeout."""
        evidence: list[str] = []

        if (
            artifact.claimed_success
            and artifact.repo_state.get("worktree_clean") is False
        ):
            evidence.append(
                "agent claimed success but worktree_clean=False — "
                "modified/untracked files remained"
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
