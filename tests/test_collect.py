"""Tests for the real-repository adapter (nemesis.collect)."""

import subprocess
from pathlib import Path

import pytest

from nemesis.__main__ import main
from nemesis.collect import collect_artifact
from nemesis.detectors.base import RunArtifact
from nemesis.detectors.declared_success_too_early import (
    DeclaredSuccessTooEarlyDetector,
)
from nemesis.detectors.dirty_worktree_after_closeout import (
    DirtyWorktreeAfterCloseoutDetector,
)


def _git(repo: Path, *args: str) -> None:
    """Run a git command in *repo* (test helper)."""
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def clean_repo(tmp_path: Path) -> Path:
    """A freshly initialized git repo with one commit and a clean worktree."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "file.txt").write_text("hello\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")
    return repo


def test_clean_repo_is_clean(clean_repo: Path) -> None:
    """A clean repo yields worktree_clean=True and no modified/untracked files."""
    artifact = collect_artifact(clean_repo)
    assert isinstance(artifact, RunArtifact)
    assert artifact.repo_state["worktree_clean"] is True
    assert artifact.repo_state["modified_files"] == []
    assert artifact.repo_state["untracked_files"] == []
    assert artifact.repo_state["branch"] == "main"
    assert artifact.repo_state["head"]  # a real commit hash


def test_dirty_repo_detected(clean_repo: Path) -> None:
    """Modified and untracked files are captured from real git state."""
    (clean_repo / "file.txt").write_text("changed\n", encoding="utf-8")
    (clean_repo / "new.tmp").write_text("junk\n", encoding="utf-8")
    artifact = collect_artifact(clean_repo)
    assert artifact.repo_state["worktree_clean"] is False
    assert "file.txt" in artifact.repo_state["modified_files"]
    assert "new.tmp" in artifact.repo_state["untracked_files"]


def test_dirty_worktree_detector_fires_on_real_state(clean_repo: Path) -> None:
    """End-to-end: a real dirty repo + claimed success trips the detector."""
    (clean_repo / "file.txt").write_text("changed\n", encoding="utf-8")
    artifact = collect_artifact(clean_repo, claimed_success=True)
    result = DirtyWorktreeAfterCloseoutDetector().detect(artifact)
    assert result.detected is True
    assert result.evidence


def test_test_results_feed_declared_success_detector(clean_repo: Path) -> None:
    """Provided failing tests + claimed success trips the flagship detector."""
    artifact = collect_artifact(
        clean_repo,
        claimed_success=True,
        test_results={"passing": False, "failed_count": 3},
    )
    assert artifact.repo_state["tests_passing"] is False
    result = DeclaredSuccessTooEarlyDetector().detect(artifact)
    assert result.detected is True


def test_tests_not_executed_without_results(clean_repo: Path) -> None:
    """Without test_results, no tests_passing key is set (Nemesis runs nothing)."""
    artifact = collect_artifact(clean_repo)
    assert "tests_passing" not in artifact.repo_state


def test_transcript_is_recorded(clean_repo: Path) -> None:
    """The provided transcript is carried onto the artifact."""
    artifact = collect_artifact(clean_repo, transcript="All done, tests pass.")
    assert artifact.transcript == "All done, tests pass."


def test_cli_check_on_clean_repo(
    clean_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`nemesis check` on a clean repo exits 0 and reports no failures."""
    exit_code = main(["check", "--repo", str(clean_repo)])
    assert exit_code == 0
    assert "No failure modes detected" in capsys.readouterr().out


def test_cli_check_detects_dirty_claimed_success(
    clean_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`nemesis check` flags a dirty worktree when success was claimed."""
    (clean_repo / "file.txt").write_text("changed\n", encoding="utf-8")
    exit_code = main(["check", "--repo", str(clean_repo), "--claimed-success"])
    assert exit_code == 0
    assert "dirty_worktree_after_closeout" in capsys.readouterr().out


def test_cli_check_writes_report(clean_repo: Path, tmp_path: Path) -> None:
    """`nemesis check --output` writes a Markdown check report."""
    out = tmp_path / "check.md"
    exit_code = main(["check", "--repo", str(clean_repo), "--output", str(out)])
    assert exit_code == 0
    assert out.read_text(encoding="utf-8").startswith("# Nemesis Check Report")
