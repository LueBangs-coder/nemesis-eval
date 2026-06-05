"""Failure-mode data model for Nemesis."""

from dataclasses import dataclass
from enum import Enum


class Category(Enum):
    VERIFICATION = "verification"
    STATE_HYGIENE = "state_hygiene"
    DOCTRINE = "doctrine"
    SCOPE = "scope"
    SKILL_DESIGN = "skill_design"


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class FailureMode:
    """A documented production failure mode from the Pantheon catalog."""

    id: str
    name: str
    category: Category
    description: str
    fix_rule: str
