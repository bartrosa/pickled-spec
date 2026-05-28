# Code context: check

- **Surface id:** pickled_bdd_check
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 5 | **Total lines:** 51 | **Truncated:** False

## Root: pickled_bdd.cli.check

```python
def check(feature_file: str, gate: str) -> None:
    """Run compensating gates against a .feature file."""
    import json as _json

    _ = gate  # v0.1: only ambiguity; "all" resolves to the same gate.
    llm = _build_llm_client()
    result = run_ambiguity_gate(feature_file, llm)
    click.echo(_json.dumps(_ambiguity_result_to_json(result), indent=2, ensure_ascii=False))
    _exit_for_verdict(result.verdict)
```

## Callee: pickled_bdd.cli._build_llm_client (hop 1)

```python
def _build_llm_client() -> LLMClient:
    """Build an LLM client. Override via PICKLED_BDD_LLM_FACTORY for tests."""
    from pickled_core.llm.bootstrap import build_default_client
    from pickled_core.llm.config import ConfigError

    try:
        return build_default_client(factory_env="PICKLED_BDD_LLM_FACTORY")
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc
```

## Callee: pickled_bdd.cli.run_ambiguity_gate (hop 1)

```python
def run_ambiguity_gate(feature_file: str | Path, llm: LLMClient | None) -> GateResult:
    """Canonical ambiguity gate entry point (CLI, alias, mine evaluate)."""
    from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
    from pickled_bdd.gates.ambiguity import AmbiguityGate

    feature = PytestBddAdapter().parse_feature_file(str(feature_file))
    if llm is None:
        return GateResult(
            gate_name="ambiguity",
            verdict=Verdict.PASS,
            notes="LLM unavailable; ambiguity gate skipped",
        )
    return AmbiguityGate(llm).run(feature)
```

## Callee: pickled_bdd.cli._ambiguity_result_to_json (hop 1)

```python
def _ambiguity_result_to_json(result: GateResult) -> dict[str, object]:
    return {
        "gate": result.gate_name,
        "verdict": result.verdict.value,
        "notes": result.notes,
        "findings": [
            {
                "scenario": f.target_name,
                "alternatives": list(f.alternatives),
                "suggested_fix": f.suggested_fix,
            }
            for f in result.findings
            if isinstance(f, AmbiguityFinding)
        ],
    }
```

## Callee: pickled_bdd.cli._exit_for_verdict (hop 1)

```python
def _exit_for_verdict(verdict: Verdict) -> None:
    import sys

    exit_codes = {Verdict.PASS: 0, Verdict.WARN: 1, Verdict.FAIL: 2}
    sys.exit(exit_codes[verdict])
```

## Unresolved callees

- `PytestBddAdapter().parse_feature_file(str(feature_file))` — receiver is a return value of unannotated callable
- `AmbiguityGate(llm).run(feature)` — receiver is a return value of unannotated callable
