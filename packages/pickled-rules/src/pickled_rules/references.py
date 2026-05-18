"""Extract rule references from Gherkin feature files via tag convention.

Tag convention: ``@<ruleset>:<rule_id>`` in Gherkin → tag string
``<ruleset>:<rule_id>`` after normalization.

- ``<ruleset>``: short name of the rule set (e.g. ``team-api-conv``).
- ``<rule_id>``: rule id verbatim (e.g. ``1.2`` or ``review-3``).

Tags without ``:`` or without a recognized shape are ignored.
"""

from __future__ import annotations

from dataclasses import dataclass

from pickled_core import Feature


@dataclass(frozen=True, slots=True)
class ScenarioReferences:
    scenario_name: str
    references: tuple[tuple[str, str], ...]
    """Pairs ``(ruleset_short_name, rule_id)``."""


def extract_references(
    feature: Feature,
    *,
    ruleset_filter: str | None = None,
) -> list[ScenarioReferences]:
    """Extract reference tags from each scenario.

    If ``ruleset_filter`` is set, only tags whose ruleset prefix matches are kept
    (comparison is case-insensitive on the ruleset side).
    """
    out: list[ScenarioReferences] = []
    for scenario in feature.scenarios:
        refs = tuple(_parse_reference_tags(scenario.tags, ruleset_filter))
        out.append(
            ScenarioReferences(
                scenario_name=scenario.name,
                references=refs,
            )
        )
    return out


def _parse_reference_tags(
    tags: tuple[str, ...],
    ruleset_filter: str | None,
) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for tag in tags:
        normalized = tag.removeprefix("@")
        if ":" not in normalized:
            continue
        ruleset, _, rule_id = normalized.partition(":")
        ruleset_key = ruleset.lower()
        if ruleset_filter is not None and ruleset_key != ruleset_filter.lower():
            continue
        if not rule_id:
            continue
        out.append((ruleset_key, rule_id))
    return out
