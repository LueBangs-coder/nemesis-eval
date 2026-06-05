"""Detector for the ``stale_local_checkout_treated_as_current`` failure mode.

The failure: the agent relied on old local files instead of verifying the true
source-of-truth repo state.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "stale_local_checkout_treated_as_current"


@register_detector
@dataclass(frozen=True)
class StaleLocalCheckoutTreatedAsCurrentDetector:
    """Detects work done on an unverified local checkout."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if the checkout was never verified against source of truth."""
        evidence: list[str] = []

        if artifact.repo_state.get("checkout_verified") is False:
            evidence.append(
                "checkout_verified=False — local files used without confirming "
                "branch/HEAD/upstream against source of truth"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
