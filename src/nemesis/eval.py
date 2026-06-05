"""The eval loop — run every registered detector against known-truth runs.

Methodology (per detector):

- One *positive* trial: the detector's own target failure is injected, so the
  detector should fire. Successes count toward the true-positive rate.
- Several *negative* trials: a clean run plus every other mode's injection, so
  the detector should stay silent. Any firing counts toward the false-positive
  rate.

A good detector scores true_positive_rate == 1.0 and false_positive_rate == 0.0.
"""

import logging
from dataclasses import dataclass, field

import nemesis.detectors  # noqa: F401  (import triggers detector registration)
from nemesis.detectors.base import Detector, all_detectors
from nemesis.test_agent import SyntheticAgent, Task

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DetectorScore:
    """The scored result of evaluating one detector.

    Attributes:
        failure_mode_id: The mode the detector targets.
        true_positive_rate: Fraction of positive trials the detector caught.
        false_positive_rate: Fraction of negative trials the detector wrongly
            flagged.
        sample_evidence: Evidence strings from the positive detection, for the
            report.
    """

    failure_mode_id: str
    true_positive_rate: float
    false_positive_rate: float
    sample_evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvalReport:
    """Aggregate results across all detectors."""

    scores: list[DetectorScore]

    @property
    def mean_true_positive_rate(self) -> float:
        """Average true-positive rate across detectors."""
        if not self.scores:
            return 0.0
        return sum(s.true_positive_rate for s in self.scores) / len(self.scores)

    @property
    def mean_false_positive_rate(self) -> float:
        """Average false-positive rate across detectors."""
        if not self.scores:
            return 0.0
        return sum(s.false_positive_rate for s in self.scores) / len(self.scores)


class EvalLoop:
    """Runs all registered detectors against synthetic known-truth runs."""

    def __init__(self, agent: SyntheticAgent | None = None) -> None:
        """Create an eval loop.

        Args:
            agent: The synthetic agent to generate artifacts. Defaults to a
                fresh ``SyntheticAgent``.
        """
        self.agent = agent or SyntheticAgent()
        self.task = Task(name="eval", description="synthetic eval task")

    def _score_detector(
        self, detector: Detector, all_mode_ids: list[str]
    ) -> DetectorScore:
        """Score one detector against its positive and negative trials."""
        target = detector.failure_mode_id

        # Positive trial: inject the detector's own target failure.
        positive_artifact = self.agent.run(self.task, inject=[target])
        positive_result = detector.detect(positive_artifact)
        true_positive_rate = 1.0 if positive_result.detected else 0.0
        if not positive_result.detected:
            logger.warning("%s missed its own injected failure", target)

        # Negative trials: a clean run plus every other mode's injection.
        negative_artifacts = [self.agent.run(self.task, inject=[])]
        negative_artifacts += [
            self.agent.run(self.task, inject=[mode_id])
            for mode_id in all_mode_ids
            if mode_id != target
        ]
        false_hits = sum(
            1 for art in negative_artifacts if detector.detect(art).detected
        )
        false_positive_rate = false_hits / len(negative_artifacts)
        if false_hits:
            logger.warning(
                "%s fired on %d/%d negative trials",
                target,
                false_hits,
                len(negative_artifacts),
            )

        return DetectorScore(
            failure_mode_id=target,
            true_positive_rate=true_positive_rate,
            false_positive_rate=false_positive_rate,
            sample_evidence=positive_result.evidence,
        )

    def run(self) -> EvalReport:
        """Run every registered detector and return the aggregate report."""
        detectors = all_detectors()
        all_mode_ids = [d.failure_mode_id for d in detectors]
        logger.info("evaluating %d detectors", len(detectors))

        scores = [self._score_detector(d, all_mode_ids) for d in detectors]
        return EvalReport(scores=scores)
