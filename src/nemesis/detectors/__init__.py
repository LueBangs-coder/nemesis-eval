"""Detectors for Pantheon failure modes.

Importing this package imports every detector module, which runs each module's
``@register_detector`` decorator and populates the registry. After importing
``nemesis.detectors``, ``nemesis.detectors.base.all_detectors()`` returns one
instance of every detector.
"""

from nemesis.detectors import (
    agent_output_not_tied_to_exact_repo_state,
    artifact_presence_not_verified,
    branch_cleanup_not_verified,
    declared_success_too_early,
    dirty_worktree_after_closeout,
    github_merge_treated_as_full_success,
    hot_file_conflict_risk,
    incomplete_implementation_prompts,
    local_status_ignored_before_next_phase,
    missing_root_doctrine_updates,
    old_session_folders_leaking_files,
    patch_vs_new_build_confusion,
    repo_drift_after_merge,
    skill_bloat,
    source_of_truth_ambiguity_across_tools,
    stale_local_checkout_treated_as_current,
    testing_without_source_verification,
    unsafe_audit_probing_language_in_prompts,
    untracked_files_appearing_unexpectedly,
    workflow_drift_across_tools,
)

__all__ = [
    "agent_output_not_tied_to_exact_repo_state",
    "artifact_presence_not_verified",
    "branch_cleanup_not_verified",
    "declared_success_too_early",
    "dirty_worktree_after_closeout",
    "github_merge_treated_as_full_success",
    "hot_file_conflict_risk",
    "incomplete_implementation_prompts",
    "local_status_ignored_before_next_phase",
    "missing_root_doctrine_updates",
    "old_session_folders_leaking_files",
    "patch_vs_new_build_confusion",
    "repo_drift_after_merge",
    "skill_bloat",
    "source_of_truth_ambiguity_across_tools",
    "stale_local_checkout_treated_as_current",
    "testing_without_source_verification",
    "unsafe_audit_probing_language_in_prompts",
    "untracked_files_appearing_unexpectedly",
    "workflow_drift_across_tools",
]
