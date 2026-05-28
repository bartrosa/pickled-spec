# Code context: run_all

- **Surface id:** pickled_bdd_run_all
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 3 | **Total lines:** 67 | **Truncated:** False

## Root: pickled_bdd.gates_runner.run_all

```python
def run_all(workdir: Path | str) -> list[GateResult]:
    """Parse Gherkin under ``features/`` (AmbiguityGate skipped without LLM)."""
    root = Path(workdir).resolve()
    features = sorted(root.glob("features/**/*.feature"))
    if not features:
        return [
            GateResult(
                gate_name="bdd.features",
                verdict=Verdict.PASS,
                notes="no features/ directory",
            )
        ]

    adapter = PytestBddAdapter()
    results: list[GateResult] = []
    for path in features:
        try:
            adapter.parse_feature_file(path)
        except Exception as exc:
            results.append(
                GateResult(
                    gate_name=f"bdd.parse.{path.name}",
                    verdict=Verdict.FAIL,
                    notes=str(exc),
                )
            )
        else:
            results.append(
                GateResult(
                    gate_name=f"bdd.parse.{path.name}",
                    verdict=Verdict.PASS,
                    notes=f"parsed {path.relative_to(root)}",
                )
            )

    results.append(
        GateResult(
            gate_name="bdd.ambiguity",
            verdict=Verdict.PASS,
            notes="skipped — set PICKLED_BDD_LLM_FACTORY to enable AmbiguityGate",
        )
    )
    return results
```

## Callee: pickled_bdd.adapters.PytestBddAdapter.parse_feature_file (hop 1)

```python
def parse_feature_file(self, path: str | Path) -> Feature:
        """Parse a `.feature` file into a runner-agnostic Feature.

        Handles Scenario, Scenario Outline, Examples, Background, and
        Rule blocks. Background steps are prepended to every scenario
        in the feature (the same expansion pytest-bdd performs at
        runtime); rule-level Background steps are appended after the
        feature-level Background for scenarios inside that rule.
        """
        p = Path(path)
        text = p.read_text(encoding="utf-8")
        return self.parse_feature_text(text, path=str(p))
```

## Callee: pickled_bdd.adapters.PytestBddAdapter.parse_feature_text (hop 2)

```python
def parse_feature_text(self, gherkin_text: str, *, path: str | None = None) -> Feature:
        """Parse a Gherkin string into a Feature.

        Same Background-prepending and feature-tag-inheritance semantics as
        :meth:`parse_feature_file`. Use ``path=None`` for in-memory content.
        """
        if not gherkin_text.strip():
            raise ValueError("Gherkin text is empty")
        ast = cast(dict[str, Any], Parser().parse(TokenScanner(gherkin_text)))
        if ast.get("feature") is None:
            raise ValueError("No Feature found in Gherkin text")
        return self._build_feature(ast, path=path)
```

## Unresolved callees

- `path.relative_to` — method name matches multiple classes; receiver type not pinned
