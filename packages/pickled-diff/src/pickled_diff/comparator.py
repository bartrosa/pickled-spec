"""Comparator protocol and default implementations."""

from __future__ import annotations

import json
from typing import Protocol, runtime_checkable

from pickled_diff.types import OracleOutput


@runtime_checkable
class Comparator(Protocol):
    """Decides whether two outputs are equivalent.

    ``compare`` returns ``(is_equal, summary)``. When ``is_equal`` is False,
    ``summary`` should be a single-line human-readable explanation of the
    difference suitable for inclusion in a DifferentialFinding.
    """

    name: str

    def compare(self, oracle: OracleOutput, candidate: OracleOutput) -> tuple[bool, str]: ...


def _error_side(oracle: OracleOutput, candidate: OracleOutput) -> str | None:
    if oracle.error:
        return f"oracle error: {oracle.error}"
    if candidate.error:
        return f"candidate error: {candidate.error}"
    return None


class ExactEqComparator:
    """Byte-exact equality of ``stdout`` strings."""

    name = "exact"

    def compare(self, oracle: OracleOutput, candidate: OracleOutput) -> tuple[bool, str]:
        err = _error_side(oracle, candidate)
        if err is not None:
            return False, err
        if oracle.stdout == candidate.stdout:
            return True, "outputs match"
        return False, "stdout differs"


class StructuralJsonComparator:
    """Equality after parsing both outputs as JSON values."""

    name = "structural_json"

    def compare(self, oracle: OracleOutput, candidate: OracleOutput) -> tuple[bool, str]:
        err = _error_side(oracle, candidate)
        if err is not None:
            return False, err
        try:
            oracle_val = json.loads(oracle.stdout)
        except json.JSONDecodeError as exc:
            return False, f"JSON parse failed (oracle): {exc}"
        try:
            candidate_val = json.loads(candidate.stdout)
        except json.JSONDecodeError as exc:
            return False, f"JSON parse failed (candidate): {exc}"
        if oracle_val == candidate_val:
            return True, "JSON values match"
        return False, "JSON values differ"


__all__ = ["Comparator", "ExactEqComparator", "StructuralJsonComparator"]
