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
    text = '''Feature: Tagged

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


def test_feature_level_tags_inherited_by_scenarios(tmp_path: Path) -> None:
    """Feature-level tags must propagate to every scenario.

    pytest-bdd applies feature-level tags as pytest marks on every
    scenario test. Downstream gates that consume `Scenario.tags` (e.g.
    pickled-rules's coverage gate, which derives rule references
    from tags) rely on the same semantics. Without this propagation, a
    feature tagged `@team-api-conv:naming.1` would yield zero references
    and the coverage gate would emit a false-FAIL verdict.
    """
    text = (
        "@smoke @team-api-conv:naming.1\n"
        "Feature: Tag inheritance\n"
        "\n"
        "  Scenario: First\n"
        "    Given x\n"
        "\n"
        "  @critical\n"
        "  Scenario: Second\n"
        "    Given y\n"
    )
    path = tmp_path / "feat_tags.feature"
    path.write_text(text, encoding="utf-8")
    feature = PytestBddAdapter().parse_feature_file(path)
    assert len(feature.scenarios) == 2
    first, second = feature.scenarios
    # Feature-level tags appear on every scenario.
    assert "smoke" in first.tags
    assert "team-api-conv:naming.1" in first.tags
    assert "smoke" in second.tags
    assert "team-api-conv:naming.1" in second.tags
    # Scenario-level tags are preserved alongside feature-level tags.
    assert "critical" in second.tags


def test_feature_level_tags_propagate_through_outline(tmp_path: Path) -> None:
    """Feature-level tags must reach every row of an expanded Outline."""
    text = (
        "@team-api-conv:errors.1\n"
        "Feature: Outline tags\n"
        "\n"
        "  Scenario Outline: Login as <role>\n"
        "    Given user role is \"<role>\"\n"
        "    Then login succeeds\n"
        "\n"
        "    Examples:\n"
        "      | role     |\n"
        "      | clinician |\n"
        "      | nurse     |\n"
    )
    path = tmp_path / "feat_outline_tags.feature"
    path.write_text(text, encoding="utf-8")
    feature = PytestBddAdapter().parse_feature_file(path)
    assert len(feature.scenarios) == 2
    for scenario in feature.scenarios:
        assert "team-api-conv:errors.1" in scenario.tags


def test_feature_level_tag_inheritance_does_not_duplicate(tmp_path: Path) -> None:
    """If a scenario already carries a feature-level tag, do not duplicate it."""
    text = (
        "@team-api-conv:naming.1\n"
        "Feature: No duplicate tags\n"
        "\n"
        "  @team-api-conv:naming.1\n"
        "  Scenario: Both levels carry the same tag\n"
        "    Given x\n"
    )
    path = tmp_path / "feat_dup_tags.feature"
    path.write_text(text, encoding="utf-8")
    feature = PytestBddAdapter().parse_feature_file(path)
    assert len(feature.scenarios) == 1
    tags = feature.scenarios[0].tags
    assert tags.count("team-api-conv:naming.1") == 1
