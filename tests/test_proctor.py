"""Tests for the proctor package."""

from __future__ import annotations

from proctor import dummy


def test_dummy() -> None:
    """Test the dummy() function."""
    assert dummy(1, 2) == 3
