# Code context: coverage_gate_features

- **Surface id:** pickled_rules_coverage_gate_features
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 4 | **Total lines:** 108 | **Truncated:** False

## Root: pickled_rules.gates.coverage.coverage_gate_features

```python
def coverage_gate_features(
    features: Sequence[Feature],
    ruleset: RuleSet,
    *,
    ruleset_short_name: str,
    artifact_ref: str | None = None,
) -> CoverageReport:
    """Compute coverage across one or more features (union of scenario tags)."""
    referenced_ids, unknown = _collect_references(
        features, ruleset, ruleset_short_name=ruleset_short_name
    )
    if artifact_ref is None:
        paths = [f.path for f in features if f.path]
        artifact_ref = ", ".join(paths) if paths else "<features>"

    referenced = tuple(r for r in ruleset.rules if r.id in referenced_ids)
    unreferenced = tuple(r for r in ruleset.rules if r.id not in referenced_ids)

    strict_unreferenced = [r for r in unreferenced if r.enforcement == "strict"]
    passed = not strict_unreferenced and not unknown

    traces = tuple(
        Trace(
            source_reference=SourceReference(
                source_id=f"{ruleset.source_id}({rule.id})",
                source_version=ruleset.source_version,
                locator=rule.id,
                description=rule.description,
                active_from=ruleset.active_from,
                applies_to=ruleset.applies_to,
                source_url=ruleset.source_url,
            ),
            artifact_kind="feature",
            artifact_ref=artifact_ref,
            relation="implements",
            confidence="asserted",
        )
        for rule in referenced
    )

    if passed:
        notes = (
            f"All strict rules in {ruleset.source_id} are referenced; no unknown reference tags."
        )
    else:
        parts: list[str] = []
        if strict_unreferenced:
            parts.append(f"{len(strict_unreferenced)} strict rule(s) unreferenced")
        if unknown:
            parts.append(f"{len(unknown)} unknown reference(s)")
        notes = "; ".join(parts) + "."

    gate_result = GateResult(
        gate_name="rules.coverage",
        verdict=Verdict.PASS if passed else Verdict.FAIL,
        findings=(),
        notes=notes,
        traces=traces,
    )

    return CoverageReport(
        referenced_rules=referenced,
        unreferenced_rules=unreferenced,
        unknown_references=tuple(sorted(unknown)),
        gate_result=gate_result,
    )
```

## Callee: pickled_rules.gates.coverage._collect_references (hop 1)

```python
def _collect_references(
    features: Sequence[Feature],
    ruleset: RuleSet,
    *,
    ruleset_short_name: str,
) -> tuple[set[str], set[tuple[str, str]]]:
    referenced_ids: set[str] = set()
    unknown: set[tuple[str, str]] = set()
    for feature in features:
        scenario_refs = extract_references(feature, ruleset_filter=ruleset_short_name)
        for sc in scenario_refs:
            for _ruleset_name, rule_id in sc.references:
                if ruleset.find(rule_id) is None:
                    unknown.add((_ruleset_name, rule_id))
                else:
                    referenced_ids.add(rule_id)
    return referenced_ids, unknown
```

## Callee: pickled_rules.references.extract_references (hop 2)

```python
def extract_references(
    feature: Feature,
    *,
    ruleset_filter: str | None = None,
) -> list[ScenarioReferences]:
    """Extract reference tags from each scenario.

    If ``ruleset_filter`` is set, only tags whose ruleset prefix matches are kept
    (comparison is case-insensitive on the ruleset side).
    """
    out: list[ScenarioReferences] = []
    for scenario in feature.scenarios:
        refs = tuple(_parse_reference_tags(scenario.tags, ruleset_filter))
        out.append(
            ScenarioReferences(
                scenario_name=scenario.name,
                references=refs,
            )
        )
    return out
```

## Callee: pickled_rules.RuleSet.find (hop 2)

```python
def find(self, rule_id: str) -> Rule | None:
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
```

## Unresolved callees

- `unknown.add` — method name matches multiple classes; receiver type not pinned
- `referenced_ids.add` — method name matches multiple classes; receiver type not pinned
