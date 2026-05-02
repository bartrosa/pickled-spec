from __future__ import annotations

from datetime import date

from pickled_core import Feature, Scenario, Verdict
from pickled_law import Corpus, CorpusRule, coverage_gate


def _tiny_corpus() -> Corpus:
    return Corpus(
        source_id="T",
        source_title="T",
        jurisdiction="g",
        authority="a",
        source_version="1",
        effective_from=date(2025, 1, 1),
        rules=(
            CorpusRule(
                id="1",
                title="R1",
                text="t1",
                obligation="required",
            ),
            CorpusRule(
                id="2",
                title="R2",
                text="t2",
                obligation="required",
            ),
            CorpusRule(
                id="3",
                title="R3",
                text="t3",
                obligation="addressable",
            ),
        ),
    )


def test_one_of_three_cited() -> None:
    corpus = _tiny_corpus()
    feat = Feature(
        name="F",
        description="",
        scenarios=(
            Scenario(name="S", steps=(), tags=("c:1",)),
        ),
        path="f.feature",
    )
    r = coverage_gate(feat, corpus, corpus_short_name="c")
    assert len(r.cited_rules) == 1
    assert len(r.uncited_rules) == 2
    assert r.unknown_citations == ()


def test_all_required_cited_passes() -> None:
    corpus = _tiny_corpus()
    feat = Feature(
        name="F",
        description="",
        scenarios=(
            Scenario(
                name="A",
                steps=(),
                tags=("c:1", "c:2"),
            ),
        ),
        path="f.feature",
    )
    r = coverage_gate(feat, corpus, corpus_short_name="c")
    assert r.gate_result.verdict == Verdict.PASS
    assert r.unknown_citations == ()


def test_required_uncited_fails() -> None:
    corpus = _tiny_corpus()
    feat = Feature(name="F", description="", scenarios=(), path="f.feature")
    r = coverage_gate(feat, corpus, corpus_short_name="c")
    assert r.gate_result.verdict == Verdict.FAIL
    assert "required" in r.gate_result.notes.lower()


def test_unknown_citation_fails() -> None:
    corpus = _tiny_corpus()
    feat = Feature(
        name="F",
        description="",
        scenarios=(Scenario(name="S", steps=(), tags=("c:99",)),),
        path="f.feature",
    )
    r = coverage_gate(feat, corpus, corpus_short_name="c")
    assert r.gate_result.verdict == Verdict.FAIL
    assert r.unknown_citations == (("c", "99"),)


def test_traces_for_cited_rules() -> None:
    corpus = _tiny_corpus()
    feat = Feature(
        name="F",
        description="",
        scenarios=(Scenario(name="S", steps=(), tags=("c:1",)),),
        path="f.feature",
    )
    r = coverage_gate(feat, corpus, corpus_short_name="c")
    assert len(r.gate_result.traces) == 1
    assert r.gate_result.traces[0].relation == "implements"
    assert r.gate_result.traces[0].confidence == "asserted"
