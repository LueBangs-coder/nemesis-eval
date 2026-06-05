"""Build a RunArtifact from a real repository plus provided run context.

**Safety:** this module runs only *read-only* git commands. It never executes
the target project's test suite or any project code — test outcomes are
accepted as input, not run. That keeps Nemesis from becoming a code-execution
vector when pointed at an untrusted repository.

This is the bridge from a real agent run to the detectors: the detectors do
not change, they just receive a RunArtifact built from observable git state
instead of from the synthetic agent.
"""

import subprocess
from pathlib import Path
from typing import Any

from nemesis.detectors.base import RunArtifact


def _git(repo_path: Path, *args: str) -> str:
    """Run a read-only git command in *repo_path* and return raw stdout.

    Uses an argument list (never a shell string), so repository contents can
    never be interpreted as commands. Output is returned unstripped — callers
    strip scalar results themselves, because the porcelain status format is
    column-sensitive (a leading space is significant).
    """
    result = subprocess.run(
        ["git", "-C", str(repo_path), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout


def collect_artifact(
    repo_path: Path,
    transcript: str = "",
    claimed_success: bool = False,
    test_results: dict[str, Any] | None = None,
) -> RunArtifact:
    """Build a RunArtifact from real, observable repository state.

    Reads git state read-only (worktree status, branch, HEAD, upstream parity).
    Test outcomes come from *test_results* if provided — this function never
    runs the project's tests.

    Args:
        repo_path: Path to a git repository to inspect.
        transcript: The agent's transcript / self-report, if available.
        claimed_success: Whether the agent declared the task complete.
        test_results: Optional mapping such as
            ``{"passing": bool, "failed_count": int}``.

    Returns:
        A RunArtifact populated from real repo state, ready for any detector.
    """
    repo_state: dict[str, Any] = {}

    # Worktree cleanliness (read-only).
    porcelain = _git(repo_path, "status", "--porcelain")
    modified: list[str] = []
    untracked: list[str] = []
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        status, name = line[:2], line[3:]
        if status == "??":
            untracked.append(name)
        else:
            modified.append(name)
    repo_state["worktree_clean"] = porcelain.strip() == ""
    repo_state["modified_files"] = modified
    repo_state["untracked_files"] = untracked

    # Branch and HEAD.
    branch = _git(repo_path, "branch", "--show-current").strip()
    repo_state["branch"] = branch or None
    head = _git(repo_path, "rev-parse", "HEAD").strip()
    repo_state["head"] = head or None

    # Upstream parity, only if an upstream is configured.
    upstream = _git(
        repo_path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"
    ).strip()
    if upstream:
        remote = _git(repo_path, "rev-parse", "@{u}").strip()
        repo_state["remote_head"] = remote or None
        repo_state["local_parity"] = bool(head) and head == remote

    # Test outcomes (provided, never executed by Nemesis).
    if test_results is not None:
        if "passing" in test_results:
            repo_state["tests_passing"] = test_results["passing"]
        if "failed_count" in test_results:
            repo_state["failed_count"] = test_results["failed_count"]

    return RunArtifact(
        transcript=transcript,
        repo_state=repo_state,
        claimed_success=claimed_success,
    )
