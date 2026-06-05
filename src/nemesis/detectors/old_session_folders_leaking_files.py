"""Detector for the ``old_session_folders_leaking_files`` failure mode.

The failure: previous session folders contained leftover generated files that
leaked into the current work.
"""

from dataclasses import dataclass

from nemesis.detectors.base import DetectionResult, RunArtifact, register_detector

FAILURE_MODE_ID = "old_session_folders_leaking_files"


@register_detector
@dataclass(frozen=True)
class OldSessionFoldersLeakingFilesDetector:
    """Detects stale files leaking from previous session folders."""

    failure_mode_id: str = FAILURE_MODE_ID

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Detect if stale session files were present."""
        evidence: list[str] = []

        if artifact.repo_state.get("stale_files_present"):
            folders = artifact.repo_state.get("stale_session_folders")
            evidence.append(
                "stale_files_present=True — leftover files from prior sessions "
                f"({folders}) were not archived or cleaned"
            )
            return DetectionResult(
                failure_mode_id=self.failure_mode_id, detected=True, evidence=evidence
            )

        return DetectionResult(
            failure_mode_id=self.failure_mode_id, detected=False, evidence=[]
        )
