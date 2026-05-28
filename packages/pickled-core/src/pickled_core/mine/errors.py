"""Actionable errors for the mining pipeline."""

from __future__ import annotations

from pathlib import Path


class MineError(Exception):
    """Base for mining pipeline errors with an actionable message."""


class MissingStageInputError(MineError):
    """A stage's required input from an earlier stage is absent."""

    def __init__(self, missing_path: Path, needed_by: str, produced_by: str) -> None:
        self.missing_path = missing_path
        self.needed_by = needed_by
        self.produced_by = produced_by
        super().__init__(
            f"{needed_by} requires {missing_path.name}, which is produced by "
            f"`pickled-spec mine {produced_by}`. Run that stage first, or use "
            f"`pickled-spec mine all` to run the whole pipeline. "
            f"(looked in: {missing_path.parent})"
        )


__all__ = ["MineError", "MissingStageInputError"]
