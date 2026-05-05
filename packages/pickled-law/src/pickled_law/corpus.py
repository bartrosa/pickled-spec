"""YAML loader for regulatory corpora."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml
from pickled_core import Citation

from pickled_law.types import (
    Corpus,
    CorpusRule,
    Obligation,
    RelationKind,
    RuleRelation,
)


class CorpusValidationError(ValueError):
    """Raised when a corpus YAML file fails schema validation."""


_VALID_OBLIGATIONS: frozenset[str] = frozenset(
    ("required", "addressable", "recommended", "informational")
)
_VALID_RELATION_KINDS: frozenset[str] = frozenset(
    ("requires_implementation_of", "supersedes", "exempts", "references")
)


def load_corpus(path: Path) -> Corpus:
    """Load a corpus from YAML.

    Raises `CorpusValidationError` on malformed input.
    """
    try:
        with path.open(encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise CorpusValidationError(f"Malformed YAML in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise CorpusValidationError(f"Corpus root must be a mapping, got {type(raw).__name__}")

    metadata_raw = _require(raw, "metadata", path)
    if not isinstance(metadata_raw, dict):
        raise CorpusValidationError(
            f"`metadata` must be a mapping in {path}, got {type(metadata_raw).__name__}"
        )
    metadata = metadata_raw

    rules_raw = _require(raw, "rules", path)

    if not isinstance(rules_raw, list):
        raise CorpusValidationError(f"`rules` must be a list in {path}")

    rules = tuple(_parse_rule(r, path) for r in rules_raw)

    source_url_raw = metadata.get("source_url")
    if source_url_raw is not None and not isinstance(source_url_raw, str):
        raise CorpusValidationError(f"`source_url` must be a string or null in {path}")

    short_name_raw = metadata.get("short_name")
    if short_name_raw is not None and not isinstance(short_name_raw, str):
        raise CorpusValidationError(f"`short_name` must be a string or null in {path}")
    short_name = short_name_raw.lower() if short_name_raw is not None else None

    return Corpus(
        source_id=_str_field(metadata, "source_id", path),
        source_title=_str_field(metadata, "source_title", path),
        jurisdiction=_str_field(metadata, "jurisdiction", path),
        authority=_str_field(metadata, "authority", path),
        source_version=_str_field(metadata, "source_version", path),
        effective_from=_parse_date(_require(metadata, "effective_from", path), path),
        source_url=source_url_raw,
        short_name=short_name,
        rules=rules,
    )


def corpus_to_citations(corpus: Corpus) -> list[Citation]:
    """Materialize each rule as a `pickled-core` `Citation`."""
    return [
        Citation(
            source_id=f"{corpus.source_id}({rule.id})",
            source_version=corpus.source_version,
            locator=rule.id,
            canonical_text=rule.text,
            effective_from=corpus.effective_from,
            jurisdiction=corpus.jurisdiction,
            source_url=corpus.source_url,
        )
        for rule in corpus.rules
    ]


def _str_field(d: dict[str, Any], key: str, path: Path) -> str:
    v = _require(d, key, path)
    if not isinstance(v, str):
        raise CorpusValidationError(f"'{key}' must be a string in {path}, got {type(v).__name__}")
    return v


def _require(d: dict[str, Any], key: str, path: Path) -> Any:
    if key not in d:
        raise CorpusValidationError(f"Missing required key '{key}' in {path}")
    return d[key]


def _parse_date(raw: Any, path: Path) -> date:
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str):
        try:
            return date.fromisoformat(raw)
        except ValueError as exc:
            raise CorpusValidationError(f"Invalid ISO date '{raw}' in {path}: {exc}") from exc
    raise CorpusValidationError(
        f"Date must be ISO string or date, got {type(raw).__name__} in {path}"
    )


def _parse_rule(raw: Any, path: Path) -> CorpusRule:
    if not isinstance(raw, dict):
        raise CorpusValidationError(f"Each rule must be a mapping in {path}")

    obligation = _require(raw, "obligation", path)
    if not isinstance(obligation, str) or obligation not in _VALID_OBLIGATIONS:
        raise CorpusValidationError(
            f"Invalid obligation {obligation!r} in {path}; "
            f"must be one of {sorted(_VALID_OBLIGATIONS)}"
        )

    relations_raw = raw.get("relations", [])
    if not isinstance(relations_raw, list):
        raise CorpusValidationError(f"`relations` must be a list in {path}")

    parent_raw = raw.get("parent")
    if parent_raw is not None and not isinstance(parent_raw, str):
        raise CorpusValidationError(f"`parent` must be a string or null in {path}")

    return CorpusRule(
        id=_str_field(raw, "id", path),
        title=_str_field(raw, "title", path),
        text=_str_field(raw, "text", path),
        obligation=cast_obligation(obligation),
        parent=parent_raw,
        relations=tuple(_parse_relation(r, path) for r in relations_raw),
    )


def _parse_relation(raw: Any, path: Path) -> RuleRelation:
    if not isinstance(raw, dict):
        raise CorpusValidationError(f"Each relation must be a mapping in {path}")
    kind = _require(raw, "kind", path)
    if not isinstance(kind, str) or kind not in _VALID_RELATION_KINDS:
        raise CorpusValidationError(
            f"Invalid relation kind {kind!r} in {path}; "
            f"must be one of {sorted(_VALID_RELATION_KINDS)}"
        )
    targets = _require(raw, "targets", path)
    if not isinstance(targets, list) or not all(isinstance(t, str) for t in targets):
        raise CorpusValidationError(f"`targets` must be a list of strings in {path}")
    return RuleRelation(kind=cast_relation_kind(kind), targets=tuple(targets))


def cast_obligation(value: str) -> Obligation:
    """Validated cast for mypy. Caller must ensure value is in the literal set."""
    assert value in _VALID_OBLIGATIONS  # noqa: S101
    return value  # type: ignore[return-value]


def cast_relation_kind(value: str) -> RelationKind:
    assert value in _VALID_RELATION_KINDS  # noqa: S101
    return value  # type: ignore[return-value]
