from __future__ import annotations

import pytest
from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter


def test_minimal_feature() -> None:
    text = "Feature: Minimal\n\n  Scenario: One\n    Given x\n"
    feature = PytestBddAdapter().parse_feature_text(text)
    assert feature.name == "Minimal"
    assert len(feature.scenarios) == 1
    assert feature.path is None


def test_background_prepended() -> None:
    text = (
        "Feature: With background\n"
        "\n"
        "  Background:\n"
        "    Given setup\n"
        "\n"
        "  Scenario: S\n"
        "    When act\n"
    )
    feature = PytestBddAdapter().parse_feature_text(text)
    steps = feature.scenarios[0].steps
    assert steps[0].startswith("Given setup")
    assert any(s.startswith("When act") for s in steps)


def test_feature_level_tag_inherited() -> None:
    text = (
        "@team-api-conv:naming.1\n"
        "Feature: Tagged\n"
        "\n"
        "  Scenario: A\n"
        "    Given x\n"
        "\n"
        "  Scenario: B\n"
        "    Given y\n"
    )
    feature = PytestBddAdapter().parse_feature_text(text)
    assert all("team-api-conv:naming.1" in s.tags for s in feature.scenarios)


def test_empty_string_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        PytestBddAdapter().parse_feature_text("   \n")
