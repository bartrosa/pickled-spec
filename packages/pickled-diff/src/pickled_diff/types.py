"""Domain types for pickled-diff."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OracleOutput:
    """The result of running an OracleRunner on one input.

    ``stdout`` is the captured output (text or serialized form, runner's choice).
    ``exit_code`` is the process exit code (0 for in-process callables).
    ``stderr`` holds diagnostic output; empty by default.
    ``error`` is non-empty iff the runner itself failed (process not started,
    timeout, etc.); in that case ``stdout`` should not be trusted.
    """

    stdout: str
    exit_code: int = 0
    stderr: str = ""
    error: str = ""


@dataclass(frozen=True)
class DifferentialFinding:
    """One input on which oracle and candidate produced different outputs.

    ``input_repr`` is a short human-readable identifier for the input
    (typically the corpus item's ``name`` or a truncated repr).
    ``oracle_output`` and ``candidate_output`` carry the comparator-relevant
    captured output strings. ``diff_summary`` is the comparator's
    one-line explanation of why the two differ.
    """

    input_repr: str
    oracle_output: str
    candidate_output: str
    diff_summary: str


__all__ = ["DifferentialFinding", "OracleOutput"]
