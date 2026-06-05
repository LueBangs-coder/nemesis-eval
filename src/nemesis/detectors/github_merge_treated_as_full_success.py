"""Detector for the ``github_merge_treated_as_full_success`` failure mode.

The failure: the process assumed "merged on GitHub" meant the operator's
local repo was ready — the remote merge was treated as full success without
verifying the local checkout.

Detection rule: the agent claimed success, the remote was merged, but the
local side was not verified.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "github_merge_treated_as_full_success"


@register_detector
@dataclass(frozen=True)
class GithubMergeTreatedAsFullSuccessDetector:
    """Detects success claimed on a remote merge without local verification."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Return whether a remote merge was treated as full success."""
        evidence: list[str] = []

        remote_merged = artifact.repo_state.get("remote_merged")
        local_verified = artifact.repo_state.get("local_verified")

        if artifact.claimed_success and remote_merged and not local_verified:
            evidence.append(
                "agent claimed success with remote_merged=True but "
                "local_verified=False — local checkout never confirmed"
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
