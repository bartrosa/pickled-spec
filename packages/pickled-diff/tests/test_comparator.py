from __future__ import annotations

from pickled_diff.comparator import (
    Comparator,
    ExactEqComparator,
    StructuralJsonComparator,
)
from pickled_diff.types import OracleOutput


def test_exact_eq_pass_on_equal_outputs() -> None:
    o = OracleOutput(stdout="same")
    eq, summary = ExactEqComparator().compare(o, o)
    assert eq is True
    assert "match" in summary


def test_exact_eq_fail_on_different_outputs() -> None:
    eq, summary = ExactEqComparator().compare(
        OracleOutput(stdout="a"),
        OracleOutput(stdout="b"),
    )
    assert eq is False
    assert "differs" in summary


def test_exact_eq_flags_oracle_error() -> None:
    eq, summary = ExactEqComparator().compare(
        OracleOutput(stdout="", error="oracle down"),
        OracleOutput(stdout="ok"),
    )
    assert eq is False
    assert "oracle" in summary


def test_exact_eq_flags_candidate_error() -> None:
    eq, summary = ExactEqComparator().compare(
        OracleOutput(stdout="ok"),
        OracleOutput(stdout="", error="candidate down"),
    )
    assert eq is False
    assert "candidate" in summary


def test_structural_json_equal_after_reformat() -> None:
    eq, _ = StructuralJsonComparator().compare(
        OracleOutput(stdout='{"a":1,"b":2}'),
        OracleOutput(stdout='{"b": 2, "a": 1}'),
    )
    assert eq is True


def test_structural_json_fail_on_value_diff() -> None:
    eq, summary = StructuralJsonComparator().compare(
        OracleOutput(stdout='{"a": 1}'),
        OracleOutput(stdout='{"a": 2}'),
    )
    assert eq is False
    assert "differ" in summary


def test_structural_json_fail_on_unparseable_oracle() -> None:
    eq, summary = StructuralJsonComparator().compare(
        OracleOutput(stdout="not json"),
        OracleOutput(stdout='{"a": 1}'),
    )
    assert eq is False
    assert "parse failed" in summary


def test_comparators_implement_protocol() -> None:
    assert isinstance(ExactEqComparator(), Comparator)
    assert isinstance(StructuralJsonComparator(), Comparator)
