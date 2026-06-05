"""Detector for the ``incomplete_implementation_prompts`` failure mode.

The failure: partial prompts created ambiguity and inconsistent execution
because scope was not fully specified.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "incomplete_implementation_prompts"


@register_detector
@dataclass(frozen=True)
class IncompleteImplementationPromptsDetector:
    """Detects work begun from an incomplete, ambiguous prompt."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if the prompt was incomplete."""
        evidence: list[str] = []

        if artifact.repo_state.get("prompt_complete") is False:
            evidence.append(
                "prompt_complete=False — work proceeded from a partial prompt "
                "lacking exact scope, files, acceptance gates, and stop conditions"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
