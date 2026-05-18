from __future__ import annotations

from datetime import date

from pickled_core import GateResult, Verdict
from pickled_rules import Rule, RuleSet, render_coverage_markdown
from pickled_rules.gates.coverage import CoverageReport


def _ruleset() -> RuleSet:
    return RuleSet(
        source_id="X",
        source_title="Test Title",
        applies_to="backend",
        maintainer="Team",
        source_version="1",
        active_from=date(2024, 1, 1),
        rules=(
            Rule(id="a", title="A|pipe", description="body", enforcement="strict"),
        ),
    )


def test_report_contains_header_and_verdict() -> None:
    rs = _ruleset()
    report = CoverageReport(
        referenced_rules=(),
        unreferenced_rules=rs.rules,
        unknown_references=(),
        gate_result=GateResult(
            gate_name="rules.coverage",
            verdict=Verdict.FAIL,
            notes="1 strict rule(s) unreferenced.",
            traces=(),
        ),
    )
    md = render_coverage_markdown(report, rs, feature_path="feat.feature")
    assert "# Coverage report" in md
    assert "Test Title" in md
    assert "## Verdict: ❌ FAIL" in md
    assert "## Referenced rules" in md
    assert "A\\|pipe" in md or "pipe" in md


def test_strict_gaps_section() -> None:
    rs = _ruleset()
    report = CoverageReport(
        referenced_rules=(),
        unreferenced_rules=rs.rules,
        unknown_references=(),
        gate_result=GateResult(
            gate_name="rules.coverage",
            verdict=Verdict.FAIL,
            notes="gap",
            traces=(),
        ),
    )
    md = render_coverage_markdown(report, rs)
    assert "## Unreferenced strict rules" in md
    assert "### `a`" in md
