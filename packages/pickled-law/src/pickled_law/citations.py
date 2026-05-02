"""Extract citations from Gherkin feature files via tag convention.

Contract: parsed features come from :class:`pickled_bdd.adapters.pytest_bdd.PytestBddAdapter`
(``parse_feature_file`` → :class:`pickled_core.Feature`). Scenario tags are normalized
without a leading ``@``.

Tag convention: ``@<corpus>:<rule_id>`` in Gherkin → tag string ``<corpus>:<rule_id>``.

- ``<corpus>``: lowercase short name (e.g. ``hipaa``).
- ``<rule_id>``: corpus rule ``id`` verbatim (e.g. ``(a)(2)(i)``).

Tags without ``:`` or without a recognized shape are ignored (normal Gherkin tags).
"""

from __future__ import annotations

from dataclasses import dataclass

from pickled_core import Feature


@dataclass(frozen=True, slots=True)
class ScenarioCitations:
    scenario_name: str
    citations: tuple[tuple[str, str], ...]
    """Pairs ``(corpus_short_name, rule_id)``."""


def extract_citations(
    feature: Feature,
    *,
    corpus_filter: str | None = None,
) -> list[ScenarioCitations]:
    """Extract citation tags from each scenario.

    If ``corpus_filter`` is set, only tags whose corpus prefix matches are kept
    (comparison is case-insensitive on the corpus side).
    """
    out: list[ScenarioCitations] = []
    for scenario in feature.scenarios:
        cites = tuple(_parse_citation_tags(scenario.tags, corpus_filter))
        out.append(
            ScenarioCitations(
                scenario_name=scenario.name,
                citations=cites,
            )
        )
    return out


def _parse_citation_tags(
    tags: tuple[str, ...],
    corpus_filter: str | None,
) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for tag in tags:
        normalized = tag.removeprefix("@")
        if ":" not in normalized:
            continue
        corpus, _, rule_id = normalized.partition(":")
        corpus_key = corpus.lower()
        if corpus_filter is not None and corpus_key != corpus_filter.lower():
            continue
        if not rule_id:
            continue
        out.append((corpus_key, rule_id))
    return out
