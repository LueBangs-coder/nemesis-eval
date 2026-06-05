"""Load the Pantheon failure-mode catalog from a YAML file."""

from pathlib import Path

import yaml

from nemesis.models import Category, FailureMode

REQUIRED_FIELDS = ("id", "name", "category", "description", "fix_rule")


def load_catalog(path: Path) -> list[FailureMode]:
    """Read the catalog YAML at *path* and return a list of FailureMode objects.

    The YAML file must be a list of mappings. Each mapping must contain the
    five required fields: id, name, category, description, fix_rule. The
    category value must match one of the Category enum members.

    Raises:
        FileNotFoundError: if *path* does not exist.
        ValueError: if any entry is missing a required field or has an
            unknown category value.
    """
    raw_text = path.read_text(encoding="utf-8")
    raw_entries = yaml.safe_load(raw_text)

    if not isinstance(raw_entries, list):
        raise ValueError(
            f"catalog at {path} must be a YAML list at the top level, "
            f"got {type(raw_entries).__name__}"
        )

    modes: list[FailureMode] = []
    for index, entry in enumerate(raw_entries):
        missing = [field for field in REQUIRED_FIELDS if field not in entry]
        if missing:
            raise ValueError(
                f"catalog entry {index} (id={entry.get('id', '?')!r}) "
                f"is missing required fields: {missing}"
            )
        try:
            category = Category(entry["category"])
        except ValueError as exc:
            raise ValueError(
                f"catalog entry {index} (id={entry['id']!r}) "
                f"has unknown category {entry['category']!r}"
            ) from exc
        modes.append(
            FailureMode(
                id=entry["id"],
                name=entry["name"],
                category=category,
                description=entry["description"],
                fix_rule=entry["fix_rule"],
            )
        )
    return modes
