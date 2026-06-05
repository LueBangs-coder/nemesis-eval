"""Detector for the ``patch_vs_new_build_confusion`` failure mode.

The failure: an agent tried to patch an old repo even though the spec had
materially changed and a new build was required.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "patch_vs_new_build_confusion"


@register_detector
@dataclass(frozen=True)
class PatchVsNewBuildConfusionDetector:
    """Detects patching chosen when a new build was required."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if patching was chosen despite a materially changed spec."""
        evidence: list[str] = []

        spec_changed = artifact.repo_state.get("spec_materially_changed")
        chose_patch = artifact.repo_state.get("chose_patch_over_rebuild")

        if spec_changed and chose_patch:
            evidence.append(
                "spec_materially_changed=True but chose_patch_over_rebuild=True — "
                "patched an old repo when a NEW BUILD was required"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
