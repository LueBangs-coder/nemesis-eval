"""Render an EvalReport as a Markdown document.

Uses plain string templating (no Jinja2) to keep the dependency surface
minimal. Lines are accumulated in a list and joined once — strings are
immutable, so repeated concatenation in a loop would copy on every step.
"""

from nemesis.detectors.base import DetectionResult
from nemesis.eval import EvalReport

BUILD_LOG_URL = "https://github.com/LueBangs-coder/nemesis-eval/blob/main/BUILD_SPEC.md"


def render_markdown(report: EvalReport) -> str:
    """Render *report* as a Markdown string.

    The document includes a summary header, a results table (per-mode
    true-positive and false-positive rates), per-detector evidence samples,
    and a link back to the Pantheon build spec.
    """
    lines: list[str] = []

    lines.append("# Nemesis Eval Report")
    lines.append("")
    lines.append(
        "Nemesis turns Pantheon's documented production failure modes into "
        "programmatic detectors. This report scores each detector against "
        "synthetic known-truth runs."
    )
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Detectors evaluated: **{len(report.scores)}**")
    lines.append(f"- Mean true-positive rate: **{report.mean_true_positive_rate:.2f}**")
    lines.append(
        f"- Mean false-positive rate: **{report.mean_false_positive_rate:.2f}**"
    )
    lines.append("")

    # Results table
    lines.append("## Results")
    lines.append("")
    lines.append("| Failure mode | TPR | FPR |")
    lines.append("| --- | --- | --- |")
    for score in report.scores:
        lines.append(
            f"| `{score.failure_mode_id}` "
            f"| {score.true_positive_rate:.2f} "
            f"| {score.false_positive_rate:.2f} |"
        )
    lines.append("")

    # Evidence samples
    lines.append("## Evidence samples")
    lines.append("")
    for score in report.scores:
        lines.append(f"### `{score.failure_mode_id}`")
        if score.sample_evidence:
            for item in score.sample_evidence:
                lines.append(f"- {item}")
        else:
            lines.append("- _(no evidence captured)_")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(
        f"Built from the failure-mode catalog. See the "
        f"[build log]({BUILD_LOG_URL})."
    )
    lines.append("")

    return "\n".join(lines)


def render_check_markdown(results: list[DetectionResult]) -> str:
    """Render the result of checking a real repository as a Markdown string.

    Unlike :func:`render_markdown` (which scores detectors on synthetic runs),
    this summarizes which failure modes were *detected* in one real run, with
    evidence for each.
    """
    fired = [r for r in results if r.detected]

    lines: list[str] = []
    lines.append("# Nemesis Check Report")
    lines.append("")
    lines.append(f"- Detectors run: **{len(results)}**")
    lines.append(f"- Failures detected: **{len(fired)}**")
    lines.append("")

    if not fired:
        lines.append("No failure modes detected in this run. ✅")
        lines.append("")
    else:
        lines.append("## Detected failures")
        lines.append("")
        for result in fired:
            lines.append(f"### `{result.failure_mode_id}`")
            for item in result.evidence:
                lines.append(f"- {item}")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"See the [build log]({BUILD_LOG_URL}).")
    lines.append("")

    return "\n".join(lines)
