from __future__ import annotations

from pickled_core import Gate, Verdict
from pickled_diff.comparator import ExactEqComparator
from pickled_diff.corpus import CorpusItem, InMemoryCorpus
from pickled_diff.gate import DifferentialOracleGate
from pickled_diff.runner import CallableRunner
from pickled_diff.types import DifferentialFinding


def test_pass_when_all_outputs_match() -> None:
    oracle = CallableRunner(lambda s: f"out:{s}")
    candidate = CallableRunner(lambda s: f"out:{s}")
    gate = DifferentialOracleGate(
        oracle=oracle,
        candidate=candidate,
        comparator=ExactEqComparator(),
    )
    corpus = InMemoryCorpus(
        [CorpusItem("a", "1"), CorpusItem("b", "2"), CorpusItem("c", "3")]
    )
    result = gate.run(corpus)
    assert result.verdict is Verdict.PASS
    assert result.findings == ()


def test_warn_when_some_outputs_mismatch() -> None:
    oracle = CallableRunner(lambda s: "same")
    candidate = CallableRunner(lambda s: "diff" if s == "2" else "same")
    gate = DifferentialOracleGate(
        oracle=oracle,
        candidate=candidate,
        comparator=ExactEqComparator(),
    )
    corpus = InMemoryCorpus(
        [CorpusItem("a", "1"), CorpusItem("b", "2"), CorpusItem("c", "3")]
    )
    result = gate.run(corpus)
    assert result.verdict is Verdict.WARN
    assert len(result.findings) == 1
    assert isinstance(result.findings[0], DifferentialFinding)


def test_fail_when_all_outputs_mismatch() -> None:
    oracle = CallableRunner(lambda _: "oracle")
    candidate = CallableRunner(lambda _: "candidate")
    gate = DifferentialOracleGate(
        oracle=oracle,
        candidate=candidate,
        comparator=ExactEqComparator(),
    )
    corpus = InMemoryCorpus(
        [CorpusItem("a", "1"), CorpusItem("b", "2"), CorpusItem("c", "3")]
    )
    result = gate.run(corpus)
    assert result.verdict is Verdict.FAIL
    assert len(result.findings) == 3


def test_fail_when_oracle_errors_on_all_inputs() -> None:
    def oracle_fail(_: str) -> str:
        raise RuntimeError("fail")

    oracle = CallableRunner(oracle_fail)
    candidate = CallableRunner(lambda s: s)
    gate = DifferentialOracleGate(
        oracle=oracle,
        candidate=candidate,
        comparator=ExactEqComparator(),
    )
    corpus = InMemoryCorpus([CorpusItem("a", "1"), CorpusItem("b", "2")])
    result = gate.run(corpus)
    assert result.verdict is Verdict.FAIL
    assert "oracle" in result.notes.lower()


def test_warn_when_oracle_errors_on_some_inputs() -> None:
    def oracle_fn(s: str) -> str:
        if s == "bad":
            raise RuntimeError("oracle fail")
        return "ok"

    oracle = CallableRunner(oracle_fn)
    candidate = CallableRunner(lambda _: "ok")
    gate = DifferentialOracleGate(
        oracle=oracle,
        candidate=candidate,
        comparator=ExactEqComparator(),
    )
    corpus = InMemoryCorpus([CorpusItem("good", "1"), CorpusItem("bad", "bad")])
    result = gate.run(corpus)
    assert result.verdict is Verdict.WARN
    assert "oracle errors" in result.notes


def test_pass_on_empty_corpus() -> None:
    gate = DifferentialOracleGate(
        oracle=CallableRunner(lambda s: s),
        candidate=CallableRunner(lambda s: s),
        comparator=ExactEqComparator(),
    )
    result = gate.run(InMemoryCorpus([]))
    assert result.verdict is Verdict.PASS
    assert "empty" in result.notes.lower()


def test_max_findings_caps_findings_list_but_not_count_in_notes() -> None:
    n = 20
    oracle = CallableRunner(lambda s: "o")
    candidate = CallableRunner(lambda s: f"c-{s}")
    gate = DifferentialOracleGate(
        oracle=oracle,
        candidate=candidate,
        comparator=ExactEqComparator(),
        max_findings=5,
    )
    corpus = InMemoryCorpus([CorpusItem(f"i{i}", str(i)) for i in range(n)])
    result = gate.run(corpus)
    assert len(result.findings) == 5
    assert f"{n}/{n} mismatches" in result.notes


def test_wrong_target_type_fails() -> None:
    gate = DifferentialOracleGate(
        oracle=CallableRunner(lambda s: s),
        candidate=CallableRunner(lambda s: s),
        comparator=ExactEqComparator(),
    )
    result = gate.run({"not": "a corpus"})
    assert result.verdict is Verdict.FAIL


def test_gate_implements_gate_protocol() -> None:
    gate = DifferentialOracleGate(
        oracle=CallableRunner(lambda s: s),
        candidate=CallableRunner(lambda s: s),
        comparator=ExactEqComparator(),
    )
    assert isinstance(gate, Gate)
