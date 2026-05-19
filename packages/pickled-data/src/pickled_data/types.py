"""Domain types for pickled-data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SQLArtifact:
    content: str
    dialect: str
    ast: Any | None = None


@dataclass(frozen=True, slots=True)
class MigrationDiff:
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)


class SQLParseError(ValueError):
    """Raised when SQL cannot be parsed."""


DBT_NOT_IMPLEMENTED_MSG = (
    "dbt support planned for v0.2 — see open question Q3 in roadmap"
)


__all__ = [
    "DBT_NOT_IMPLEMENTED_MSG",
    "MigrationDiff",
    "SQLArtifact",
    "SQLParseError",
]
