"""Tests for nemesis.catalog.load_catalog."""

from pathlib import Path

import pytest

from nemesis.catalog import load_catalog
from nemesis.models import Category, FailureMode


CATALOG_PATH = Path(__file__).parent.parent / "data" / "failure_modes.yaml"

EXPECTED_MODE_COUNT = 20

REQUIRED_FIELDS = ("id", "name", "category", "description", "fix_rule")


@pytest.fixture
def catalog() -> list[FailureMode]:
    """The full catalog loaded from data/failure_modes.yaml."""
    return load_catalog(CATALOG_PATH)


def test_catalog_loads_exactly_twenty_modes(catalog: list[FailureMode]) -> None:
    """The catalog must contain exactly twenty failure modes."""
    assert len(catalog) == EXPECTED_MODE_COUNT


def test_every_mode_has_all_required_fields(catalog: list[FailureMode]) -> None:
    """Every mode must have non-empty values for all required fields."""
    for mode in catalog:
        for field in REQUIRED_FIELDS:
            value = getattr(mode, field)
            assert value, f"mode {mode.id!r} has empty {field!r}"


def test_every_mode_category_is_an_enum_member(catalog: list[FailureMode]) -> None:
    """The category field must be a Category enum, not a raw string."""
    for mode in catalog:
        assert isinstance(
            mode.category, Category
        ), f"mode {mode.id!r} has non-enum category: {mode.category!r}"


def test_all_mode_ids_are_unique(catalog: list[FailureMode]) -> None:
    """No two modes may share an id."""
    ids = [mode.id for mode in catalog]
    assert len(ids) == len(set(ids)), "duplicate ids found in catalog"


def test_load_catalog_missing_file_raises(tmp_path: Path) -> None:
    """Loading a non-existent path must raise FileNotFoundError."""
    missing = tmp_path / "does_not_exist.yaml"
    with pytest.raises(FileNotFoundError):
        load_catalog(missing)


def test_load_catalog_rejects_unknown_category(tmp_path: Path) -> None:
    """Loading a catalog with an invalid category must raise ValueError."""
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text(
        "- id: x\n"
        "  name: X\n"
        "  category: not_a_real_category\n"
        "  description: d\n"
        "  fix_rule: f\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unknown category"):
        load_catalog(bad_file)


def test_load_catalog_rejects_missing_required_field(tmp_path: Path) -> None:
    """Loading a catalog with a missing required field must raise ValueError."""
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text(
        "- id: x\n"
        "  name: X\n"
        "  category: verification\n"
        "  description: d\n",  # fix_rule missing
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing required fields"):
        load_catalog(bad_file)
