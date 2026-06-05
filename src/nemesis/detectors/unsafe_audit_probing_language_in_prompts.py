"""Detector for the ``unsafe_audit_probing_language_in_prompts`` failure mode.

The failure: some prompts used wording that could be misread as security
probing instead of public-access-only language.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "unsafe_audit_probing_language_in_prompts"


@register_detector
@dataclass(frozen=True)
class UnsafeAuditProbingLanguageInPromptsDetector:
    """Detects probing-style language in prompts."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if probing-style language was present in a prompt."""
        evidence: list[str] = []

        if artifact.repo_state.get("probing_language_present"):
            evidence.append(
                "probing_language_present=True — prompt wording could read as "
                "security probing rather than public-access-only language"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
