"""Synthetic test agent — produces RunArtifacts with known failures injected.

The :class:`SyntheticAgent` is a controllable fake agent. You hand it a
:class:`Task` and a list of failure-mode ids to inject; it returns a
:class:`RunArtifact` that genuinely exhibits each requested failure.

Design:

- Each failure mode has a :class:`FailureSignature` — a data record describing
  how that failure manifests in an artifact (transcript marker, repo_state
  delta, optional claimed_success override).
- Injection applies a signature; :func:`manifests` checks the real fields show
  it. This is ground-truth by construction: we know the failure is present
  because we built the artifact to exhibit it.
- The registry maps mode id -> signature (the Strategy pattern). Adding a mode
  means adding one signature entry, never editing :meth:`SyntheticAgent.run`.

Note on the module name: BUILD_SPEC.md specifies ``src/nemesis/test_agent.py``.
A source module prefixed ``test_`` would normally collide with pytest's
discovery, but ``[tool.pytest.ini_options] testpaths = ["tests"]`` confines
collection to the tests/ tree, so this module is never collected as tests.
"""

from dataclasses import dataclass, field, replace
from typing import Any

from nemesis.detectors.base import RunArtifact

FailureModeId = str


@dataclass(frozen=True)
class Task:
    """A synthetic task the agent pretends to work on.

    Attributes:
        name: Short identifier for the task.
        description: What the task is nominally about.
    """

    name: str
    description: str = ""


@dataclass(frozen=True)
class FailureSignature:
    """How a single failure mode manifests in a RunArtifact.

    Attributes:
        mode_id: The failure mode id this signature injects.
        transcript_marker: Text appended to the transcript to reflect the
            failure in the agent's self-report.
        repo_state_delta: Keys/values merged into repo_state to reflect the
            observable ground-truth side of the failure.
        claimed_success: If not ``None``, overrides the artifact's
            claimed_success flag.
    """

    mode_id: FailureModeId
    transcript_marker: str
    repo_state_delta: dict[str, Any] = field(default_factory=dict)
    claimed_success: bool | None = None


# ─── Failure signatures — one per catalog mode ───────────────────────────────
# Each signature is grounded in the mode's description in data/failure_modes.yaml.

_SIGNATURE_LIST: list[FailureSignature] = [
    # Verification and ground truth
    FailureSignature(
        "agent_declared_success_too_early",
        "All tests passing. Task complete.",
        {"tests_passing": False, "failed_count": 2},
        claimed_success=True,
    ),
    FailureSignature(
        "stale_local_checkout_treated_as_current",
        "Working from local files; looks up to date.",
        {"local_head": "abc123", "remote_head": "def456", "checkout_verified": False},
    ),
    FailureSignature(
        "source_of_truth_ambiguity_across_tools",
        "GitHub looks merged; assuming that is authoritative.",
        {"canonical_source_declared": False, "sources_disagree": True},
    ),
    FailureSignature(
        "github_merge_treated_as_full_success",
        "PR merged on GitHub — calling this done.",
        {"remote_merged": True, "local_verified": False},
        claimed_success=True,
    ),
    FailureSignature(
        "repo_drift_after_merge",
        "Merge complete.",
        {"remote_head": "def456", "local_head": "abc123", "local_parity": False},
    ),
    FailureSignature(
        "artifact_presence_not_verified",
        "Generated the report. Done.",
        {"expected_artifacts": ["report.md"], "artifacts_present": False},
        claimed_success=True,
    ),
    FailureSignature(
        "agent_output_not_tied_to_exact_repo_state",
        "Tests passed.",
        {"branch": None, "head": None, "report_includes_repo_state": False},
    ),
    FailureSignature(
        "testing_without_source_verification",
        "Ran the tests, all green.",
        {"tests_passing": True, "source_verified": False, "tested_branch": "unknown"},
    ),
    # State hygiene and closeout
    FailureSignature(
        "dirty_worktree_after_closeout",
        "Phase complete.",
        {
            "worktree_clean": False,
            "modified_files": ["a.py"],
            "untracked_files": ["b.tmp"],
        },
        claimed_success=True,
    ),
    FailureSignature(
        "old_session_folders_leaking_files",
        "Continuing from prior session.",
        {"stale_session_folders": [".old_session/"], "stale_files_present": True},
    ),
    FailureSignature(
        "branch_cleanup_not_verified",
        "Merged the branch.",
        {"branch_merged": True, "branch_deleted": False},
    ),
    FailureSignature(
        "local_status_ignored_before_next_phase",
        "Starting the next phase.",
        {"previous_phase_closed": False, "closeout_checks_run": False},
    ),
    FailureSignature(
        "untracked_files_appearing_unexpectedly",
        "Wrapping up.",
        {"untracked_files": ["mystery.out"], "untracked_explained": False},
    ),
    # Doctrine and multi-agent coordination
    FailureSignature(
        "missing_root_doctrine_updates",
        "Changed the skill behavior.",
        {"behavior_changed": True, "root_docs_updated": False},
    ),
    FailureSignature(
        "hot_file_conflict_risk",
        "Editing CLAUDE.md.",
        {"hot_file_touched": "CLAUDE.md", "coordination_gate": False},
    ),
    FailureSignature(
        "workflow_drift_across_tools",
        "Following my own conventions.",
        {"shared_doctrine_followed": False, "tools_disagree": True},
    ),
    # Scope and specification
    FailureSignature(
        "patch_vs_new_build_confusion",
        "Patching the old repo to fit the new spec.",
        {"spec_materially_changed": True, "chose_patch_over_rebuild": True},
    ),
    FailureSignature(
        "incomplete_implementation_prompts",
        "Got a partial prompt; guessing the rest.",
        {"prompt_complete": False, "scope_ambiguous": True},
    ),
    # Skill design and prompt safety
    FailureSignature(
        "skill_bloat",
        "Adding more to this skill.",
        {"skill_line_count": 1200, "skill_is_portable": False},
    ),
    FailureSignature(
        "unsafe_audit_probing_language_in_prompts",
        "Probing the target for weaknesses.",
        {"public_access_only_language": False, "probing_language_present": True},
    ),
]

SIGNATURES: dict[FailureModeId, FailureSignature] = {
    sig.mode_id: sig for sig in _SIGNATURE_LIST
}


def _clean_artifact(task: Task) -> RunArtifact:
    """A baseline artifact representing a run with no failures."""
    return RunArtifact(
        transcript=f"Working on task: {task.name}.",
        repo_state={"tests_passing": True},
        claimed_success=False,
    )


def _apply_signature(artifact: RunArtifact, sig: FailureSignature) -> RunArtifact:
    """Return a new artifact mutated to exhibit *sig*'s failure."""
    new_transcript = f"{artifact.transcript} {sig.transcript_marker}".strip()
    new_repo_state = {**artifact.repo_state, **sig.repo_state_delta}
    new_claimed = (
        sig.claimed_success
        if sig.claimed_success is not None
        else artifact.claimed_success
    )
    return replace(
        artifact,
        transcript=new_transcript,
        repo_state=new_repo_state,
        claimed_success=new_claimed,
    )


def manifests(artifact: RunArtifact, mode_id: FailureModeId) -> bool:
    """Return True if *artifact* genuinely exhibits *mode_id*'s failure.

    Checks the real artifact fields against the mode's signature: the
    transcript marker is present, every repo_state delta key/value matches,
    and (if the signature sets it) claimed_success matches.
    """
    sig = SIGNATURES[mode_id]
    if sig.transcript_marker not in artifact.transcript:
        return False
    for key, value in sig.repo_state_delta.items():
        if artifact.repo_state.get(key) != value:
            return False
    if (
        sig.claimed_success is not None
        and artifact.claimed_success != sig.claimed_success
    ):
        return False
    return True


class SyntheticAgent:
    """A controllable fake agent that injects known failures on demand."""

    def run(self, task: Task, inject: list[FailureModeId] | None = None) -> RunArtifact:
        """Produce a RunArtifact for *task*, injecting each failure in *inject*.

        Args:
            task: The synthetic task being "worked on".
            inject: Failure-mode ids to inject. ``None`` or empty produces a
                clean artifact with no failures.

        Returns:
            A RunArtifact that genuinely exhibits each injected failure.

        Raises:
            KeyError: if an id in *inject* has no registered signature.
        """
        artifact = _clean_artifact(task)
        for mode_id in inject or []:
            if mode_id not in SIGNATURES:
                raise KeyError(f"no failure signature registered for {mode_id!r}")
            artifact = _apply_signature(artifact, SIGNATURES[mode_id])
        return artifact

    @property
    def supported_modes(self) -> list[FailureModeId]:
        """The failure-mode ids this agent can inject."""
        return list(SIGNATURES.keys())
