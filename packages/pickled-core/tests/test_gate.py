from __future__ import annotations

from pickled_core import Gate, GateResult, Verdict


class SimpleGate:
    """Minimal structural implementation of `Gate` for protocol checks."""

    name = "simple"

    def run(
        self,
        target: object,
        *,
        context: dict[str, object] | None = None,
    ) -> GateResult:
        _ = target, context
        return GateResult(gate_name=self.name, verdict=Verdict.PASS)


def test_gate_protocol_runtime_checkable() -> None:
    gate = SimpleGate()
    assert isinstance(gate, Gate)
