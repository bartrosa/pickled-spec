"""Tests for :class:`pickled_rules.drafter.RuleSetDrafter`."""

from __future__ import annotations

from pickled_bdd.testing import CannedLLMClient
from pickled_rules.drafter import RATIONALE_SENTINEL, RuleSetDrafter
from pickled_rules.loader import load_ruleset_from_text

_VALID_RULESET = """metadata:
  source_id: test-src
  source_title: Test Rules
  applies_to: internal-api
  maintainer: tests
  source_version: '1.0'
  active_from: '2026-05-25'
rules:
  - id: api-naming
    title: Use consistent paths
    description: REST paths use kebab-case resource names.
    enforcement: strict
"""


def _with_rationale(body: str, rationale: str = "One rule for naming.") -> str:
    return f"{body.strip()}\n{RATIONALE_SENTINEL}\n{rationale}"


def test_drafts_valid_yaml_from_brief() -> None:
    llm = CannedLLMClient(_with_rationale(_VALID_RULESET))
    result = RuleSetDrafter(llm).draft_from_brief(
        brief_text="API naming rules",
        ruleset_short_name="api",
        source_id="test-src",
        applies_to="internal-api",
        active_from="2026-05-25",
    )
    load_ruleset_from_text(result.text)
    assert result.warnings == ()
    assert result.rationale == "One rule for naming."


def test_warns_on_malformed_yaml() -> None:
    broken = "metadata: [\nrules: []\n"
    llm = CannedLLMClient(_with_rationale(broken))
    result = RuleSetDrafter(llm).draft_from_brief(
        brief_text="x",
        ruleset_short_name="api",
        source_id="test-src",
        applies_to="internal-api",
        active_from="2026-05-25",
    )
    assert result.text.strip().startswith("metadata:")
    assert len(result.warnings) >= 1


def test_warns_on_forbidden_token() -> None:
    bad = _VALID_RULESET.replace(
        "REST paths use kebab-case resource names.",
        "REST paths must follow compliance program wording.",
    )
    llm = CannedLLMClient(_with_rationale(bad))
    result = RuleSetDrafter(llm).draft_from_brief(
        brief_text="x",
        ruleset_short_name="api",
        source_id="test-src",
        applies_to="internal-api",
        active_from="2026-05-25",
    )
    assert any("forbidden token" in w for w in result.warnings)


def test_handles_missing_rationale_sentinel() -> None:
    llm = CannedLLMClient(_VALID_RULESET)
    result = RuleSetDrafter(llm).draft_from_brief(
        brief_text="x",
        ruleset_short_name="api",
        source_id="test-src",
        applies_to="internal-api",
        active_from="2026-05-25",
    )
    assert result.rationale == ""
    assert "api-naming" in result.text
