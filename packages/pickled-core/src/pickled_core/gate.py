"""Gate protocol — the interface every compensating gate implements."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pickled_core.types import GateResult


@runtime_checkable
class Gate(Protocol):
    """A compensating gate.

    Implementations evaluate a target (a parsed Feature, an OpenAPI spec,
    a Rego policy, ...) and return a `GateResult`. The target is typed as
    `object` here because gates from different packages target different
    types; each package's gate constructor narrows this.
    """

    name: str

    def run(
        self,
        target: object,
        *,
        context: dict[str, object] | None = None,
    ) -> GateResult:
        """Evaluate `target` and return a verdict."""
        ...
