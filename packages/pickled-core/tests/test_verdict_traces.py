"""Traces attach to :class:`GateResult`, not the :class:`Verdict` enum."""

from __future__ import annotations

from datetime import date

from pickled_core import GateResult, SourceReference, Trace, Verdict


def _trace() -> Trace:
    ref = SourceReference(
        source_id="INTERNAL-CHK-1",
        source_version="v1",
        locator="review-3",
        description="Every change includes a test update.",
        active_from=date(2024, 1, 1),
        applies_to="all-services",
    )
    return Trace(
        source_reference=ref,
        artifact_kind="feature",
        artifact_ref="features/x.feature",
        relation="implements",
        confidence="asserted",
    )


def test_gate_result_default_traces_is_empty_tuple() -> None:
    assert GateResult(gate_name="g", verdict=Verdict.PASS).traces == ()


def test_gate_result_with_traces_equality() -> None:
    t = _trace()
    a = GateResult(gate_name="ambiguity", verdict=Verdict.PASS, traces=(t,))
    b = GateResult(gate_name="ambiguity", verdict=Verdict.PASS, traces=(t,))
    assert a == b


def test_gate_result_traces_are_hashable_when_frozen() -> None:
    t = _trace()
    a = GateResult(gate_name="g", verdict=Verdict.WARN, traces=(t,))
    b = GateResult(gate_name="g", verdict=Verdict.WARN, traces=(t,))
    assert len({a, b}) == 1


def test_gate_result_back_compat_positional() -> None:
    """Same positional shape as before traces existed."""
    r = GateResult("my-gate", Verdict.PASS)
    assert r.gate_name == "my-gate"
    assert r.verdict == Verdict.PASS
    assert r.findings == ()
    assert r.notes == ""
    assert r.traces == ()


def test_gate_result_back_compat_keyword() -> None:
    r = GateResult(gate_name="g", verdict=Verdict.FAIL)
    assert r.traces == ()
