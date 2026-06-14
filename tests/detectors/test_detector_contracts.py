"""Per-detector contract tests.

Unlike the eval loop (which drives detectors with the ``SyntheticAgent`` that
injects failures), these build ``RunArtifact`` objects by hand. That tests each
detector's contract directly and avoids circularity with the agent that
generates the eval fixtures.

Each registered detector must:
1. fire (with evidence) on an artifact carrying its own signal, and
2. stay silent on a clean, empty artifact.

The ``test_every_detector_has_a_contract_case`` guard fails if a detector is
added without a corresponding case here, so coverage cannot silently regress.
"""

import pytest

import nemesis.detectors  # noqa: F401  (importing registers every detector)
from nemesis.detectors.base import RunArtifact, all_detectors

# failure_mode_id -> (claimed_success, repo_state) that MUST trip the detector.
FIRING_CASES: dict[str, tuple[bool, dict]] = {
    "agent_output_not_tied_to_exact_repo_state": (
        False,
        {"report_includes_repo_state": False},
    ),
    "artifact_presence_not_verified": (
        True,
        {"artifacts_present": False, "expected_artifacts": ["dist/pkg.whl"]},
    ),
    "branch_cleanup_not_verified": (
        False,
        {"branch_merged": True, "branch_deleted": False},
    ),
    "agent_declared_success_too_early": (
        True,
        {"tests_passing": False, "failed_count": 3},
    ),
    "dirty_worktree_after_closeout": (True, {"worktree_clean": False}),
    "github_merge_treated_as_full_success": (
        True,
        {"remote_merged": True, "local_verified": False},
    ),
    "hot_file_conflict_risk": (
        False,
        {"hot_file_touched": True, "coordination_gate": False},
    ),
    "incomplete_implementation_prompts": (False, {"prompt_complete": False}),
    "local_status_ignored_before_next_phase": (
        False,
        {"previous_phase_closed": False},
    ),
    "missing_root_doctrine_updates": (
        False,
        {"behavior_changed": True, "root_docs_updated": False},
    ),
    "old_session_folders_leaking_files": (
        False,
        {"stale_files_present": True, "stale_session_folders": ["_old"]},
    ),
    "patch_vs_new_build_confusion": (
        False,
        {"spec_materially_changed": True, "chose_patch_over_rebuild": True},
    ),
    "repo_drift_after_merge": (False, {"local_parity": False}),
    "skill_bloat": (False, {"skill_is_portable": False, "skill_line_count": 900}),
    "source_of_truth_ambiguity_across_tools": (
        False,
        {"sources_disagree": True, "canonical_source_declared": False},
    ),
    "stale_local_checkout_treated_as_current": (False, {"checkout_verified": False}),
    "testing_without_source_verification": (
        False,
        {"source_verified": False, "tested_branch": "old"},
    ),
    "unsafe_audit_probing_language_in_prompts": (
        False,
        {"probing_language_present": True},
    ),
    "untracked_files_appearing_unexpectedly": (
        False,
        {"untracked_files": ["scratch.tmp"], "untracked_explained": False},
    ),
    "workflow_drift_across_tools": (False, {"shared_doctrine_followed": False}),
}


def _detector_for(mode_id: str):
    """Return the single registered detector for *mode_id*."""
    for detector in all_detectors():
        if detector.failure_mode_id == mode_id:
            return detector
    raise AssertionError(f"no detector registered for {mode_id!r}")


def test_every_detector_has_a_contract_case() -> None:
    """Every registered detector must be covered by a firing case here."""
    registered = {d.failure_mode_id for d in all_detectors()}
    assert registered == set(FIRING_CASES), (
        f"missing cases: {registered - set(FIRING_CASES)} | "
        f"unknown cases: {set(FIRING_CASES) - registered}"
    )


@pytest.mark.parametrize("mode_id", sorted(FIRING_CASES))
def test_detector_fires_on_its_signal(mode_id: str) -> None:
    """A detector fires, with evidence, on an artifact carrying its signal."""
    claimed_success, repo_state = FIRING_CASES[mode_id]
    artifact = RunArtifact(
        transcript="", repo_state=repo_state, claimed_success=claimed_success
    )
    result = _detector_for(mode_id).detect(artifact)
    assert result.detected is True
    assert result.evidence, "a positive detection must carry evidence"
    assert result.failure_mode_id == mode_id


@pytest.mark.parametrize("mode_id", sorted(FIRING_CASES))
def test_detector_silent_on_clean_artifact(mode_id: str) -> None:
    """A detector stays silent on a clean, empty artifact."""
    clean = RunArtifact(transcript="", repo_state={}, claimed_success=False)
    result = _detector_for(mode_id).detect(clean)
    assert result.detected is False
