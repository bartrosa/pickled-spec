from __future__ import annotations

from pickled_core import Feature, Scenario
from pickled_rules.references import ScenarioReferences, extract_references


def _feat(scenarios: tuple[Scenario, ...]) -> Feature:
    return Feature(name="F", description="", scenarios=scenarios, path="x.feature")


def test_two_reference_tags() -> None:
    s = Scenario(
        name="List users",
        steps=("Given x",),
        tags=("team-api-conv:naming.1", "team-api-conv:errors.1"),
    )
    got = extract_references(_feat((s,)), ruleset_filter="team-api-conv")
    assert got == [
        ScenarioReferences(
            scenario_name="List users",
            references=(("team-api-conv", "naming.1"), ("team-api-conv", "errors.1")),
        )
    ]


def test_no_reference_tags() -> None:
    s = Scenario(name="S", steps=("Given x",), tags=("smoke",))
    assert extract_references(_feat((s,)))[0].references == ()


def test_mixed_tags_and_filter() -> None:
    s = Scenario(
        name="S",
        steps=(),
        tags=("smoke", "team-api-conv:naming.1", "other-set:rule-1"),
    )
    assert extract_references(_feat((s,)), ruleset_filter="team-api-conv")[0].references == (
        ("team-api-conv", "naming.1"),
    )


def test_leading_at_stripped() -> None:
    s = Scenario(name="S", steps=(), tags=("@team-api-conv:naming.1",))
    refs = extract_references(_feat((s,)), ruleset_filter="team-api-conv")[0].references
    assert refs == (("team-api-conv", "naming.1"),)
