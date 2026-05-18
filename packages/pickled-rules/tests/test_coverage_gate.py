from __future__ import annotations

from datetime import date

from pickled_core import Feature, Scenario, Verdict
from pickled_rules import Rule, RuleSet, coverage_gate


def _tiny_ruleset() -> RuleSet:
    return RuleSet(
        source_id="T",
        source_title="T",
        applies_to="global",
        maintainer="tests",
        source_version="1",
        active_from=date(2025, 1, 1),
        rules=(
            Rule(id="1", title="R1", description="t1", enforcement="strict"),
            Rule(id="2", title="R2", description="t2", enforcement="strict"),
            Rule(id="3", title="R3", description="t3", enforcement="advisory"),
        ),
    )


def test_one_of_three_referenced() -> None:
    rs = _tiny_ruleset()
    feat = Feature(
        name="F",
        description="",
        scenarios=(Scenario(name="S", steps=(), tags=("r:1",)),),
        path="f.feature",
    )
    r = coverage_gate(feat, rs, ruleset_short_name="r")
    assert len(r.referenced_rules) == 1
    assert len(r.unreferenced_rules) == 2


def test_all_strict_referenced_passes() -> None:
    rs = _tiny_ruleset()
    feat = Feature(
        name="F",
        description="",
        scenarios=(Scenario(name="A", steps=(), tags=("r:1", "r:2")),),
        path="f.feature",
    )
    r = coverage_gate(feat, rs, ruleset_short_name="r")
    assert r.gate_result.verdict == Verdict.PASS


def test_strict_unreferenced_fails() -> None:
    rs = _tiny_ruleset()
    feat = Feature(name="F", description="", scenarios=(), path="f.feature")
    r = coverage_gate(feat, rs, ruleset_short_name="r")
    assert r.gate_result.verdict == Verdict.FAIL
    assert "strict" in r.gate_result.notes.lower()


def test_unknown_reference_fails() -> None:
    rs = _tiny_ruleset()
    feat = Feature(
        name="F",
        description="",
        scenarios=(Scenario(name="S", steps=(), tags=("r:99",)),),
        path="f.feature",
    )
    r = coverage_gate(feat, rs, ruleset_short_name="r")
    assert r.gate_result.verdict == Verdict.FAIL
    assert r.unknown_references == (("r", "99"),)


def test_advisory_unreferenced_does_not_fail() -> None:
    rs = _tiny_ruleset()
    feat = Feature(
        name="F",
        description="",
        scenarios=(Scenario(name="S", steps=(), tags=("r:1", "r:2")),),
        path="f.feature",
    )
    r = coverage_gate(feat, rs, ruleset_short_name="r")
    assert r.gate_result.verdict == Verdict.PASS


def test_traces_for_referenced_rules() -> None:
    rs = _tiny_ruleset()
    feat = Feature(
        name="F",
        description="",
        scenarios=(Scenario(name="S", steps=(), tags=("r:1",)),),
        path="f.feature",
    )
    r = coverage_gate(feat, rs, ruleset_short_name="r")
    assert len(r.gate_result.traces) == 1
    assert r.gate_result.traces[0].relation == "implements"
    assert r.gate_result.traces[0].source_reference.locator == "1"
