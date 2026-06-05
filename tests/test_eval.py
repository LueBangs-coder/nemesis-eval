"""End-to-end tests for the eval loop and CLI."""

from pathlib import Path

import pytest

from nemesis.catalog import load_catalog
from nemesis.detectors.base import all_detectors
from nemesis.eval import EvalLoop, EvalReport
from nemesis.__main__ import main

CATALOG_PATH = Path(__file__).parent.parent / "data" / "failure_modes.yaml"


@pytest.fixture
def report() -> EvalReport:
    """The eval report from a full run."""
    return EvalLoop().run()


def test_at_least_fifteen_detectors_registered() -> None:
    """The phase requires detectors for at least 15 of the 20 modes."""
    assert len(all_detectors()) >= 15


def test_every_detector_targets_a_real_catalog_mode() -> None:
    """Each detector's failure_mode_id must exist in the catalog."""
    catalog_ids = {mode.id for mode in load_catalog(CATALOG_PATH)}
    for detector in all_detectors():
        assert detector.failure_mode_id in catalog_ids


def test_report_has_one_score_per_detector(report: EvalReport) -> None:
    """The report scores every registered detector."""
    assert len(report.scores) == len(all_detectors())


def test_every_detector_catches_its_own_failure(report: EvalReport) -> None:
    """True-positive rate must be 1.0 for every detector."""
    for score in report.scores:
        assert (
            score.true_positive_rate == 1.0
        ), f"{score.failure_mode_id} missed its own injected failure"


def test_no_detector_false_positives(report: EvalReport) -> None:
    """False-positive rate must be 0.0 for every detector."""
    for score in report.scores:
        assert (
            score.false_positive_rate == 0.0
        ), f"{score.failure_mode_id} fired on a negative trial"


def test_positive_detections_carry_evidence(report: EvalReport) -> None:
    """Every caught failure must include at least one evidence string."""
    for score in report.scores:
        assert score.sample_evidence, f"{score.failure_mode_id} produced no evidence"


def test_mean_rates(report: EvalReport) -> None:
    """Aggregate rates reflect a clean run: mean TPR 1.0, mean FPR 0.0."""
    assert report.mean_true_positive_rate == 1.0
    assert report.mean_false_positive_rate == 0.0


def test_cli_eval_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    """`nemesis eval` exits 0 and prints a report."""
    exit_code = main(["eval"])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "detector scores" in out
    assert "mean TPR" in out


def test_cli_requires_a_command() -> None:
    """Invoking with no subcommand exits non-zero (argparse error)."""
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code != 0
