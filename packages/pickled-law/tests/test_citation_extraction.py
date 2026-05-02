from __future__ import annotations

from pickled_core import Feature, Scenario
from pickled_law.citations import ScenarioCitations, extract_citations


def _feat(scenarios: tuple[Scenario, ...]) -> Feature:
    return Feature(name="F", description="", scenarios=scenarios, path="x.feature")


def test_two_citation_tags() -> None:
    s = Scenario(
        name="Login",
        steps=("Given x",),
        tags=("hipaa:(a)(2)(i)", "hipaa:(d)"),
    )
    got = extract_citations(_feat((s,)), corpus_filter="hipaa")
    assert got == [
        ScenarioCitations(
            scenario_name="Login",
            citations=(("hipaa", "(a)(2)(i)"), ("hipaa", "(d)")),
        )
    ]


def test_no_citation_tags() -> None:
    s = Scenario(name="S", steps=("Given x",), tags=("smoke",))
    got = extract_citations(_feat((s,)))
    assert got[0].citations == ()


def test_mixed_tags_and_filter() -> None:
    s = Scenario(
        name="S",
        steps=(),
        tags=("smoke", "hipaa:(b)", "gdpr:art5"),
    )
    assert extract_citations(_feat((s,)), corpus_filter="hipaa")[0].citations == (("hipaa", "(b)"),)
    assert extract_citations(_feat((s,)))[0].citations == (("hipaa", "(b)"), ("gdpr", "art5"))


def test_leading_at_stripped() -> None:
    s = Scenario(name="S", steps=(), tags=("@hipaa:(a)(1)",))
    cites = extract_citations(_feat((s,)), corpus_filter="hipaa")[0].citations
    assert cites == (("hipaa", "(a)(1)"),)
