"""Detector for the ``source_of_truth_ambiguity_across_tools`` failure mode.

The failure: it was unclear whether GitHub, the local repo, or a tool session
was authoritative, and the sources disagreed.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "source_of_truth_ambiguity_across_tools"


@register_detector
@dataclass(frozen=True)
class SourceOfTruthAmbiguityAcrossToolsDetector:
    """Detects disagreeing sources with no declared canonical checkout."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if sources disagree and no canonical source was declared."""
        evidence: list[str] = []

        sources_disagree = artifact.repo_state.get("sources_disagree")
        canonical_declared = artifact.repo_state.get("canonical_source_declared")

        if sources_disagree and not canonical_declared:
            evidence.append(
                "sources_disagree=True but canonical_source_declared=False — "
                "no authoritative checkout to verify against"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
