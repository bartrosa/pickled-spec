# Code context: verify

- **Surface id:** pickled_diff_verify
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 4 | **Total lines:** 156 | **Truncated:** False

## Root: pickled_diff.cli.verify

```python
def verify(
    oracle: str,
    candidate: str,
    corpus: Path,
    comparator: str,
    timeout_seconds: float,
) -> None:
    """Compare candidate vs reference across a JSON input corpus."""
    raw = json.loads(corpus.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise click.ClickException("Corpus JSON must be a list of {name, payload} objects")
    items = [
        CorpusItem(name=str(entry["name"]), payload=str(entry["payload"]))
        for entry in raw
        if isinstance(entry, dict)
    ]
    gate = DifferentialOracleGate(
        oracle=SubprocessRunner(
            shlex.split(oracle),
            name="oracle",
            timeout_seconds=timeout_seconds,
        ),
        candidate=SubprocessRunner(
            shlex.split(candidate),
            name="candidate",
            timeout_seconds=timeout_seconds,
        ),
        comparator=_comparator(comparator),
    )
    result = gate.run(InMemoryCorpus(items))
    click.echo(json.dumps(_gate_result_to_json(result), indent=2, ensure_ascii=False))
    exit_codes = {Verdict.PASS: 0, Verdict.WARN: 1, Verdict.FAIL: 2}
    sys.exit(exit_codes[result.verdict])
```

## Callee: pickled_diff.cli._comparator (hop 1)

```python
def _comparator(name: str) -> ExactEqComparator | StructuralJsonComparator:
    if name == "structural_json":
        return StructuralJsonComparator()
    return ExactEqComparator()
```

## Callee: pickled_diff.DifferentialOracleGate.run (hop 1)

```python
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
```

## Callee: pickled_diff.cli._gate_result_to_json (hop 1)

```python
def _gate_result_to_json(result: Any) -> dict[str, Any]:
    from pickled_diff.types import DifferentialFinding

    return {
        "gate": result.gate_name,
        "verdict": result.verdict.value,
        "notes": result.notes,
        "findings": [
            {
                "input_repr": f.input_repr,
                "oracle_output": f.oracle_output,
                "candidate_output": f.candidate_output,
                "diff_summary": f.diff_summary,
            }
            for f in result.findings
            if isinstance(f, DifferentialFinding)
        ],
    }
```

## Unresolved callees

- `getattr(target, '_pickled_diff_corpus', False)` — dynamic attribute access
- `self._oracle.run` — protocol or unknown attribute type
- `self._candidate.run` — protocol or unknown attribute type
- `self._comparator.compare` — protocol or unknown attribute type
