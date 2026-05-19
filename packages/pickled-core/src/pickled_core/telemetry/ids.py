"""Run identifier generation."""

from __future__ import annotations

from ulid import ULID


def generate_run_id() -> str:
    """Return a new ULID string suitable for run directory names."""
    return str(ULID())


__all__ = ["generate_run_id"]
