"""Command-line entry point for Nemesis.

Two subcommands:

- ``nemesis eval`` scores every detector against synthetic known-truth runs
  (the demo / self-test).
- ``nemesis check`` runs the detectors against a *real* repository, building
  the artifact from read-only git state (the real-run tool).

Python runs this file when the package is invoked with ``-m``.
"""

import argparse
import logging
import sys
from pathlib import Path

import nemesis.detectors  # noqa: F401  (import registers all detectors)
from nemesis.collect import collect_artifact
from nemesis.detectors.base import all_detectors
from nemesis.eval import EvalLoop, EvalReport
from nemesis.report import render_check_markdown, render_markdown

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


def _run_check(args: argparse.Namespace) -> int:
    """Build an artifact from a real repo and report any detected failures.

    Returns ``1`` when ``--fail-on-detect`` was given and at least one failure
    mode fired (so the command can gate CI); ``0`` otherwise.
    """
    transcript = ""
    if args.transcript is not None:
        transcript = args.transcript.read_text(encoding="utf-8")

    test_results = None
    if args.tests_passing is not None:
        test_results = {"passing": args.tests_passing == "true"}

    artifact = collect_artifact(
        args.repo,
        transcript=transcript,
        claimed_success=args.claimed_success,
        test_results=test_results,
    )
    results = [detector.detect(artifact) for detector in all_detectors()]
    fired = [r for r in results if r.detected]

    if args.output is not None:
        args.output.write_text(render_check_markdown(results), encoding="utf-8")
        logger.info("wrote check report to %s", args.output)
    else:
        print("=" * 72)
        print(f"Nemesis check — {args.repo}")
        print("=" * 72)
        if not fired:
            print("No failure modes detected.")
        else:
            for result in fired:
                print(f"DETECTED: {result.failure_mode_id}")
                for line in result.evidence:
                    print(f"    evidence: {line}")
        print("-" * 72)
        print(f"detectors run: {len(results)}   failures detected: {len(fired)}")
        print("=" * 72)

    if args.fail_on_detect and fired:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch the requested subcommand.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code (0 on success).
    """
    # Make console output crash-proof on consoles that can't encode every
    # character (e.g. Windows cp1252). Reports written to files use UTF-8.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError):  # pragma: no cover
            pass

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

    check_parser = subparsers.add_parser(
        "check", help="run detectors against a real repository (read-only git)"
    )
    check_parser.add_argument(
        "--repo",
        type=Path,
        default=Path("."),
        help="path to the git repository to inspect (default: current directory)",
    )
    check_parser.add_argument(
        "--transcript",
        type=Path,
        default=None,
        help="path to a file containing the agent transcript",
    )
    check_parser.add_argument(
        "--claimed-success",
        action="store_true",
        help="record that the agent declared the task complete",
    )
    check_parser.add_argument(
        "--tests-passing",
        choices=["true", "false"],
        default=None,
        help="provide the test outcome (Nemesis never runs the tests itself)",
    )
    check_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="write a Markdown report to this path instead of printing to stdout",
    )
    check_parser.add_argument(
        "--fail-on-detect",
        action="store_true",
        help="exit with a non-zero status if any failure mode is detected "
        "(use this to gate CI)",
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

    if args.command == "check":
        return _run_check(args)

    parser.error(f"unknown command: {args.command}")
    return 2  # pragma: no cover  (argparse exits before reaching here)


if __name__ == "__main__":
    sys.exit(main())
