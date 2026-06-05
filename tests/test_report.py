"""Tests for the Markdown report renderer and the --output CLI flag."""

from pathlib import Path

import pytest

from nemesis.__main__ import main
from nemesis.eval import EvalLoop
from nemesis.report import render_markdown


@pytest.fixture
def markdown() -> str:
    """A rendered report from a full eval run."""
    return render_markdown(EvalLoop().run())


def test_report_has_title_and_summary(markdown: str) -> None:
    """The report starts with a title and a summary section."""
    assert markdown.startswith("# Nemesis Eval Report")
    assert "## Summary" in markdown
    assert "Mean true-positive rate" in markdown


def test_report_has_results_table(markdown: str) -> None:
    """The report includes a Markdown results table with a header row."""
    assert "| Failure mode | TPR | FPR |" in markdown
    assert "| --- | --- | --- |" in markdown


def test_report_lists_every_detector(markdown: str) -> None:
    """Every scored detector appears in the report."""
    for score in EvalLoop().run().scores:
        assert f"`{score.failure_mode_id}`" in markdown


def test_report_links_to_build_spec(markdown: str) -> None:
    """The report footer links back to the Pantheon build spec."""
    assert "BUILD_SPEC.md" in markdown


def test_cli_output_flag_writes_file(tmp_path: Path) -> None:
    """`nemesis eval --output PATH` writes a Markdown report to PATH."""
    out = tmp_path / "report.md"
    exit_code = main(["eval", "--output", str(out)])
    assert exit_code == 0
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Nemesis Eval Report")
    assert "## Results" in text


def test_cli_without_output_flag_still_prints(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`nemesis eval` with no --output still prints to stdout (unchanged)."""
    exit_code = main(["eval"])
    assert exit_code == 0
    assert "detector scores" in capsys.readouterr().out
