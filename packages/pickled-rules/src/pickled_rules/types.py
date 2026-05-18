"""Data types for YAML rule sets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pickled_core import SourceReference

Enforcement = Literal["strict", "advisory", "informational"]
RelationKind = Literal[
    "requires_implementation_of",
    "supersedes",
    "overrides",
    "references",
]


@dataclass(frozen=True, slots=True)
class RuleRelation:
    kind: RelationKind
    targets: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Rule:
    id: str
    title: str
    description: str
    enforcement: Enforcement
    parent: str | None = None
    relations: tuple[RuleRelation, ...] = ()


@dataclass(frozen=True, slots=True)
class RuleSet:
    source_id: str
    source_title: str
    applies_to: str
    maintainer: str
    source_version: str
    active_from: date
    rules: tuple[Rule, ...]
    source_url: str | None = None

    def find(self, rule_id: str) -> Rule | None:
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None

    def as_references(self) -> list[SourceReference]:
        """Materialize each rule as a :class:`pickled_core.SourceReference`."""
        from pickled_rules.loader import ruleset_to_references

        return ruleset_to_references(self)
