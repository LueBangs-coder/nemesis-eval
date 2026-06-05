"""Command-line entry point for Nemesis.

Enables ``python -m nemesis eval``. Python runs this file when the package is
invoked with ``-m``.
"""

import argparse
import logging
import sys
from pathlib import Path

from nemesis.eval import EvalLoop, EvalReport
from nemesis.report import render_markdown

logger = logging.getLogger(__name__)


def _print_report(report: EvalReport) -> None:
    """Print a human-readable summary of an eval report to stdout."""
    print("=" * 72)
    print("Nemesis eval — detector scores")
    print("=" * 72)
    for score in report.scores:
        print(
            f"{score.failure_mode_id:<42} "
            f"TPR={score.true_positive_rate:.2f}  "
            f"FPR={score.false_positive_rate:.2f}"
        )
        for line in score.sample_evidence:
            print(f"    evidence: {line}")
    print("-" * 72)
    print(
        f"detectors: {len(report.scores)}   "
        f"mean TPR: {report.mean_true_positive_rate:.2f}   "
        f"mean FPR: {report.mean_false_positive_rate:.2f}"
    )
    print("=" * 72)


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch the requested subcommand.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code (0 on success).
    """
    parser = argparse.ArgumentParser(prog="nemesis", description="Nemesis eval harness")
    subparsers = parser.add_subparsers(dest="command", required=True)
    eval_parser = subparsers.add_parser(
        "eval", help="run all detectors against known-truth runs"
    )
    eval_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="write a Markdown report to this path instead of printing to stdout",
    )

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s %(name)s: %(message)s"
    )

    if args.command == "eval":
        report = EvalLoop().run()
        if args.output is not None:
            args.output.write_text(render_markdown(report), encoding="utf-8")
            logger.info("wrote report to %s", args.output)
        else:
            _print_report(report)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2  # pragma: no cover  (argparse exits before reaching here)


if __name__ == "__main__":
    sys.exit(main())
