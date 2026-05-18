"""YAML loader for rule sets."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml
from pickled_core import SourceReference

from pickled_rules.types import (
    Enforcement,
    RelationKind,
    Rule,
    RuleRelation,
    RuleSet,
)


class RuleSetValidationError(ValueError):
    """Raised when a rule set YAML file fails schema validation."""


_VALID_ENFORCEMENT: frozenset[str] = frozenset(("strict", "advisory", "informational"))
_VALID_RELATION_KINDS: frozenset[str] = frozenset(
    ("requires_implementation_of", "supersedes", "overrides", "references")
)


def load_ruleset(path: Path) -> RuleSet:
    """Load a rule set from YAML.

    Raises `RuleSetValidationError` on malformed input.
    """
    try:
        with path.open(encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise RuleSetValidationError(f"Malformed YAML in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise RuleSetValidationError(
            f"Rule set root must be a mapping, got {type(raw).__name__}"
        )

    metadata_raw = _require(raw, "metadata", path)
    if not isinstance(metadata_raw, dict):
        raise RuleSetValidationError(
            f"`metadata` must be a mapping in {path}, got {type(metadata_raw).__name__}"
        )
    metadata = metadata_raw

    rules_raw = _require(raw, "rules", path)
    if not isinstance(rules_raw, list):
        raise RuleSetValidationError(f"`rules` must be a list in {path}")

    rules = tuple(_parse_rule(r, path) for r in rules_raw)

    source_url_raw = metadata.get("source_url")
    if source_url_raw is not None and not isinstance(source_url_raw, str):
        raise RuleSetValidationError(f"`source_url` must be a string or null in {path}")

    return RuleSet(
        source_id=_str_field(metadata, "source_id", path),
        source_title=_str_field(metadata, "source_title", path),
        applies_to=_str_field(metadata, "applies_to", path),
        maintainer=_str_field(metadata, "maintainer", path),
        source_version=_str_field(metadata, "source_version", path),
        active_from=_parse_date(_require(metadata, "active_from", path), path),
        source_url=source_url_raw,
        rules=rules,
    )


def ruleset_to_references(ruleset: RuleSet) -> list[SourceReference]:
    """Materialize each rule as a `pickled-core` `SourceReference`."""
    return [
        SourceReference(
            source_id=f"{ruleset.source_id}({rule.id})",
            source_version=ruleset.source_version,
            locator=rule.id,
            description=rule.description,
            active_from=ruleset.active_from,
            applies_to=ruleset.applies_to,
            source_url=ruleset.source_url,
        )
        for rule in ruleset.rules
    ]


def _str_field(d: dict[str, Any], key: str, path: Path) -> str:
    v = _require(d, key, path)
    if not isinstance(v, str):
        raise RuleSetValidationError(
            f"'{key}' must be a string in {path}, got {type(v).__name__}"
        )
    return v


def _require(d: dict[str, Any], key: str, path: Path) -> Any:
    if key not in d:
        raise RuleSetValidationError(f"Missing required key '{key}' in {path}")
    return d[key]


def _parse_date(raw: Any, path: Path) -> date:
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str):
        try:
            return date.fromisoformat(raw)
        except ValueError as exc:
            raise RuleSetValidationError(
                f"Invalid ISO date '{raw}' in {path}: {exc}"
            ) from exc
    raise RuleSetValidationError(
        f"Date must be ISO string or date, got {type(raw).__name__} in {path}"
    )


def _parse_rule(raw: Any, path: Path) -> Rule:
    if not isinstance(raw, dict):
        raise RuleSetValidationError(f"Each rule must be a mapping in {path}")

    enforcement = _require(raw, "enforcement", path)
    if not isinstance(enforcement, str) or enforcement not in _VALID_ENFORCEMENT:
        raise RuleSetValidationError(
            f"Invalid enforcement {enforcement!r} in {path}; "
            f"must be one of {sorted(_VALID_ENFORCEMENT)}"
        )

    relations_raw = raw.get("relations", [])
    if not isinstance(relations_raw, list):
        raise RuleSetValidationError(f"`relations` must be a list in {path}")

    parent_raw = raw.get("parent")
    if parent_raw is not None and not isinstance(parent_raw, str):
        raise RuleSetValidationError(f"`parent` must be a string or null in {path}")

    return Rule(
        id=_str_field(raw, "id", path),
        title=_str_field(raw, "title", path),
        description=_str_field(raw, "description", path),
        enforcement=cast_enforcement(enforcement),
        parent=parent_raw,
        relations=tuple(_parse_relation(r, path) for r in relations_raw),
    )


def _parse_relation(raw: Any, path: Path) -> RuleRelation:
    if not isinstance(raw, dict):
        raise RuleSetValidationError(f"Each relation must be a mapping in {path}")
    kind = _require(raw, "kind", path)
    if not isinstance(kind, str) or kind not in _VALID_RELATION_KINDS:
        raise RuleSetValidationError(
            f"Invalid relation kind {kind!r} in {path}; "
            f"must be one of {sorted(_VALID_RELATION_KINDS)}"
        )
    targets = _require(raw, "targets", path)
    if not isinstance(targets, list) or not all(isinstance(t, str) for t in targets):
        raise RuleSetValidationError(f"`targets` must be a list of strings in {path}")
    return RuleRelation(kind=cast_relation_kind(kind), targets=tuple(targets))


def cast_enforcement(value: str) -> Enforcement:
    assert value in _VALID_ENFORCEMENT  # noqa: S101
    return value  # type: ignore[return-value]


def cast_relation_kind(value: str) -> RelationKind:
    assert value in _VALID_RELATION_KINDS  # noqa: S101
    return value  # type: ignore[return-value]
