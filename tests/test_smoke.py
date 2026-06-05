"""Smoke test — verifies the package imports without crashing."""

import nemesis


def test_nemesis_imports():
    """The nemesis package can be imported."""
    assert nemesis is not None
