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
