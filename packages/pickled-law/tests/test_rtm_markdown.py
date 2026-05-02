from __future__ import annotations

from datetime import date

from pickled_core import GateResult, Verdict
from pickled_law import Corpus, CorpusRule, render_rtm_markdown
from pickled_law.gates.coverage import CoverageReport


def _corpus() -> Corpus:
    return Corpus(
        source_id="X",
        source_title="Test Title",
        jurisdiction="US",
        authority="Auth",
        source_version="1",
        effective_from=date(2024, 1, 1),
        source_url="https://example.com",
        rules=(
            CorpusRule(id="a", title="A|pipe", text="body", obligation="required"),
        ),
    )


def test_rtm_contains_header_and_verdict() -> None:
    corpus = _corpus()
    report = CoverageReport(
        cited_rules=(),
        uncited_rules=corpus.rules,
        unknown_citations=(),
        gate_result=GateResult(
            gate_name="law.coverage",
            verdict=Verdict.FAIL,
            notes="1 required rule(s) uncited.",
            traces=(),
        ),
    )
    md = render_rtm_markdown(report, corpus, feature_path="feat.feature")
    assert "# Requirements Traceability Matrix" in md
    assert "Test Title" in md
    assert "## Verdict: ❌ FAIL" in md
    assert "## Coverage" in md
    assert r"A\|pipe" in md or "pipe" in md


def test_required_gaps_section() -> None:
    corpus = _corpus()
    report = CoverageReport(
        cited_rules=(),
        uncited_rules=corpus.rules,
        unknown_citations=(),
        gate_result=GateResult(
            gate_name="law.coverage",
            verdict=Verdict.FAIL,
            notes="gap",
            traces=(),
        ),
    )
    md = render_rtm_markdown(report, corpus)
    assert "## Required gaps" in md
    assert "### `a`" in md
