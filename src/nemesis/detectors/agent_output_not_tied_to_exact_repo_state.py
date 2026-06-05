"""Detector for the ``agent_output_not_tied_to_exact_repo_state`` failure mode.

The failure: reports lacked enough detail to prove what commit or branch was
tested — output was not tied to an exact repo state.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "agent_output_not_tied_to_exact_repo_state"


@register_detector
@dataclass(frozen=True)
class AgentOutputNotTiedToExactRepoStateDetector:
    """Detects a report that does not cite the exact repo state tested."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if the report omits branch/HEAD/repo-state detail."""
        evidence: list[str] = []

        if artifact.repo_state.get("report_includes_repo_state") is False:
            evidence.append(
                "report_includes_repo_state=False — output cannot prove which "
                "branch/HEAD/commit was tested"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
