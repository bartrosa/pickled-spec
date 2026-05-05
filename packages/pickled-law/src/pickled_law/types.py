"""Data types for regulatory corpora."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pickled_core import Citation

Obligation = Literal["required", "addressable", "recommended", "informational"]
RelationKind = Literal[
    "requires_implementation_of",
    "supersedes",
    "exempts",
    "references",
]


@dataclass(frozen=True, slots=True)
class RuleRelation:
    kind: RelationKind
    targets: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CorpusRule:
    id: str
    title: str
    text: str
    obligation: Obligation
    parent: str | None = None
    relations: tuple[RuleRelation, ...] = ()


@dataclass(frozen=True, slots=True)
class Corpus:
    source_id: str
    source_title: str
    jurisdiction: str
    authority: str
    source_version: str
    effective_from: date
    rules: tuple[CorpusRule, ...]
    source_url: str | None = None
    short_name: str | None = None
    """Tag-convention prefix used in scenario citation tags.

    Tags use the form ``@<short_name>:<rule_id>``. Declaring this on the
    corpus itself decouples the convention from filesystem layout — the
    CLI no longer has to guess from the YAML filename when a corpus is
    loaded via ``--corpus-path``. Always normalised to lowercase.
    """

    def find(self, rule_id: str) -> CorpusRule | None:
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None

    def as_citations(self) -> list[Citation]:
        """Materialize each rule as a :class:`pickled_core.Citation`."""
        from pickled_law.corpus import corpus_to_citations

        return corpus_to_citations(self)
