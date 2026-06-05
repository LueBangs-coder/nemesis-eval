"""Base types every Nemesis detector uses.

Three shapes:

- ``RunArtifact``: the input — what the agent produced (transcript, repo
  state, claimed success).
- ``DetectionResult``: the output — whether the failure occurred and the
  evidence behind the verdict.
- ``Detector``: the Protocol every detector implementation satisfies. No
  explicit inheritance required.
"""

from dataclasses import dataclass
from typing import Any, Protocol, TypeVar


@dataclass(frozen=True)
class RunArtifact:
    """A snapshot of one agent run that detectors inspect.

    Attributes:
        transcript: The agent's final transcript or self-report (free text).
        repo_state: A snapshot of observable ground truth from the checkout
            (test results, file presence, branch status, etc.). Keys are
            stable identifiers documented per detector that consumes them.
        claimed_success: Whether the agent declared the task complete.
    """

    transcript: str
    repo_state: dict[str, Any]
    claimed_success: bool


@dataclass(frozen=True)
class DetectionResult:
    """The outcome of one detector inspecting one RunArtifact.

    Attributes:
        failure_mode_id: Identifier of the failure mode this result is about
            (matches a ``FailureMode.id`` in the catalog).
        detected: ``True`` if the failure was observed; ``False`` otherwise.
        evidence: Human-readable strings explaining the verdict. Should never
            be empty for positive detections (``detected=True``).
    """

    failure_mode_id: str
    detected: bool
    evidence: list[str]


class Detector(Protocol):
    """The interface every detector satisfies.

    A class satisfies this Protocol implicitly: no explicit inheritance is
    required. As long as a class declares the matching attribute and method
    signatures, static type checkers (mypy, pyright, ruff) treat it as a
    Detector wherever one is expected.
    """

    failure_mode_id: str

    def detect(self, artifact: RunArtifact) -> DetectionResult:
        """Inspect the artifact and return whether the target failure occurred."""
        ...


# ─── Detector registry ───────────────────────────────────────────────────────
# Detectors register themselves with the @register_detector decorator. The eval
# loop calls all_detectors() to get one instance of every registered detector,
# so it never has to name them individually.

_DETECTOR_REGISTRY: list[type] = []

DetectorClass = TypeVar("DetectorClass")


def register_detector(cls: DetectorClass) -> DetectorClass:
    """Decorator: add *cls* to the detector registry and return it unchanged."""
    _DETECTOR_REGISTRY.append(cls)
    return cls


def all_detectors() -> list[Detector]:
    """Instantiate and return one of every registered detector."""
    return [cls() for cls in _DETECTOR_REGISTRY]
