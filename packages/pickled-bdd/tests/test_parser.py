from __future__ import annotations

from pathlib import Path

from pickled_bdd import PytestBddAdapter

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
PASSWORD_FEATURE = EXAMPLES_DIR / "password_reset.feature"


def test_parse_example_feature_name() -> None:
    adapter = PytestBddAdapter()
    feature = adapter.parse_feature_file(PASSWORD_FEATURE)
    assert feature.name == "Password reset via email"


def test_four_scenarios_after_outline_expansion() -> None:
    adapter = PytestBddAdapter()
    feature = adapter.parse_feature_file(PASSWORD_FEATURE)
    assert len(feature.scenarios) == 4


def test_background_prepended_to_all_scenarios() -> None:
    adapter = PytestBddAdapter()
    feature = adapter.parse_feature_file(PASSWORD_FEATURE)
    bg = "Given the password reset service is available"
    for sc in feature.scenarios:
        assert sc.steps[0] == bg


def test_scenario_outline_substitution() -> None:
    adapter = PytestBddAdapter()
    feature = adapter.parse_feature_file(PASSWORD_FEATURE)
    outline_scenarios = [
        s
        for s in feature.scenarios
        if "ghost@example.com" in "".join(s.steps)
    ]
    assert len(outline_scenarios) == 1
    sc = outline_scenarios[0]
    joined = "\n".join(sc.steps)
    assert "ghost@example.com" in joined
    assert "unregistered" in joined
    assert "<email>" not in joined
    assert "<status>" not in joined


def test_tag_extraction() -> None:
    adapter = PytestBddAdapter()
    text = '''@smoke
Feature: Tagged

  @critical
  Scenario: One
    Given x
'''
    path = Path(__file__).resolve().parent / "_tagged.feature"
    path.write_text(text, encoding="utf-8")
    try:
        feature = adapter.parse_feature_file(path)
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].tags == ("critical",)
    finally:
        path.unlink(missing_ok=True)


def test_rule_block_scenarios_are_emitted(tmp_path: Path) -> None:
    """Scenarios nested under ``Rule:`` must not be silently dropped.

    Critical for downstream gates that consume scenario tags (e.g. the
    pickled-law coverage gate, where dropped scenarios would mean
    dropped regulatory citations and a falsely-failing compliance run).
    """
    adapter = PytestBddAdapter()
    text = '''Feature: F
  Background:
    Given the system is running

  Rule: A
    Background:
      Given an audit log exists

    @hipaa:(a)(2)(i)
    Scenario: S1
      Given I am a user
      When I act
      Then it works
'''
    path = tmp_path / "rule.feature"
    path.write_text(text, encoding="utf-8")

    feature = adapter.parse_feature_file(path)

    assert len(feature.scenarios) == 1
    sc = feature.scenarios[0]
    assert sc.name == "S1"
    assert sc.tags == ("hipaa:(a)(2)(i)",)
    assert sc.steps == (
        "Given the system is running",
        "Given an audit log exists",
        "Given I am a user",
        "When I act",
        "Then it works",
    )


def test_rule_tags_are_inherited_by_child_scenarios(tmp_path: Path) -> None:
    adapter = PytestBddAdapter()
    text = '''Feature: F

  @rule_tag
  Rule: R

    @scen_tag
    Scenario: S
      Given x
'''
    path = tmp_path / "rule_tags.feature"
    path.write_text(text, encoding="utf-8")

    feature = adapter.parse_feature_file(path)

    assert len(feature.scenarios) == 1
    assert feature.scenarios[0].tags == ("rule_tag", "scen_tag")


def test_rule_block_supports_scenario_outline(tmp_path: Path) -> None:
    adapter = PytestBddAdapter()
    text = '''Feature: F

  Rule: R

    Scenario Outline: S
      Given action <a>

      Examples:
        | a |
        | x |
        | y |
'''
    path = tmp_path / "rule_outline.feature"
    path.write_text(text, encoding="utf-8")

    feature = adapter.parse_feature_file(path)

    assert len(feature.scenarios) == 2
    assert feature.scenarios[0].steps == ("Given action x",)
    assert feature.scenarios[1].steps == ("Given action y",)
