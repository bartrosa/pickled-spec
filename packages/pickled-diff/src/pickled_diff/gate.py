"""DifferentialOracleGate — reference vs candidate across a corpus."""

from __future__ import annotations

from typing import Any

from pickled_core import GateResult, Verdict

from pickled_diff.comparator import Comparator
from pickled_diff.corpus import Corpus
from pickled_diff.runner import OracleRunner
from pickled_diff.types import DifferentialFinding


class DifferentialOracleGate:
    """Compensating gate: compares oracle and candidate outputs across a corpus.

    Verdict semantics:
    - PASS: comparator reports equality on every compared corpus item.
    - WARN: at least one mismatch but not all; or the oracle errored on some
      (not all) inputs.
    - FAIL: every compared item mismatches; or the oracle errored on every input.

    The gate does NOT take an LLMClient. Comparison is deterministic by design.
    """

    name = "differential.oracle"

    def __init__(
        self,
        *,
        oracle: OracleRunner,
        candidate: OracleRunner,
        comparator: Comparator,
        max_findings: int = 10,
    ) -> None:
        self._oracle = oracle
        self._candidate = candidate
        self._comparator = comparator
        self._max_findings = max_findings

    def run(
        self,
        target: object,
        *,
        context: dict[str, Any] | None = None,
    ) -> GateResult:
        _ = context
        if not isinstance(target, Corpus) or not getattr(
            target, "_pickled_diff_corpus", False
        ):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected InMemoryCorpus (Corpus), got {type(target).__name__}",
            )

        total = len(target)
        if total == 0:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.PASS,
                notes="Corpus is empty; nothing to verify.",
            )

        findings: list[DifferentialFinding] = []
        oracle_errors = 0
        candidate_errors = 0
        compared = 0
        mismatches = 0

        for item in target:
            oracle_out = self._oracle.run(item.payload)
            if oracle_out.error:
                oracle_errors += 1
                continue

            candidate_out = self._candidate.run(item.payload)
            if candidate_out.error:
                candidate_errors += 1
                compared += 1
                mismatches += 1
                if len(findings) < self._max_findings:
                    findings.append(
                        DifferentialFinding(
                            input_repr=item.name,
                            oracle_output=oracle_out.stdout,
                            candidate_output=candidate_out.stdout,
                            diff_summary=f"candidate error: {candidate_out.error}",
                        )
                    )
                continue

            compared += 1
            equal, summary = self._comparator.compare(oracle_out, candidate_out)
            if not equal:
                mismatches += 1
                if len(findings) < self._max_findings:
                    findings.append(
                        DifferentialFinding(
                            input_repr=item.name,
                            oracle_output=oracle_out.stdout,
                            candidate_output=candidate_out.stdout,
                            diff_summary=summary,
                        )
                    )

        notes = (
            f"{mismatches}/{compared} mismatches among compared items "
            f"(corpus size {total}); "
            f"{oracle_errors} oracle errors; {candidate_errors} candidate errors."
        )

        if oracle_errors == total:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                findings=tuple(findings),
                notes=notes + " Oracle failed on every input — check oracle configuration.",
            )

        if compared == 0:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                findings=tuple(findings),
                notes=notes,
            )

        if mismatches == compared:
            verdict = Verdict.FAIL
        elif mismatches > 0 or oracle_errors > 0:
            verdict = Verdict.WARN
        else:
            verdict = Verdict.PASS

        return GateResult(
            gate_name=self.name,
            verdict=verdict,
            findings=tuple(findings),
            notes=notes,
        )


__all__ = ["DifferentialOracleGate"]
