# Code context: run_all

- **Surface id:** pickled_rules_run_all
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 7 | **Total lines:** 274 | **Truncated:** True

## Root: pickled_rules.gates_runner.run_all

```python
def run_all(workdir: Path | str) -> list[GateResult]:
    """Run coverage gate for each feature against ``pickled.ruleset.yaml``."""
    root = Path(workdir).resolve()
    cfg = _workdir_config(root)
    try:
        entries = _resolve_ruleset_entries(root, cfg)
    except RuleSetValidationError as exc:
        return [
            GateResult(
                gate_name="rules.coverage",
                verdict=Verdict.FAIL,
                notes=str(exc),
            )
        ]

    if not entries:
        return [
            GateResult(
                gate_name="rules.coverage",
                verdict=Verdict.WARN,
                notes="missing pickled.ruleset.yaml or ruleset/rulesets key",
            )
        ]

    feature_pattern = _feature_glob(cfg)
    features = sorted(root.glob(feature_pattern))
    if not features:
        return [
            GateResult(
                gate_name="rules.coverage",
                verdict=Verdict.WARN,
                notes="no feature files",
            )
        ]

    adapter = PytestBddAdapter()
    parsed = [adapter.parse_feature_file(path) for path in features]

    results: list[GateResult] = []
    for entry in entries:
        gate_name = (
            "rules.coverage"
            if len(entries) == 1
            else f"rules.coverage.{entry.short_name}"
        )
        if not entry.path.is_file():
            results.append(
                GateResult(
                    gate_name=gate_name,
                    verdict=Verdict.FAIL,
                    notes=f"ruleset not found: {entry.path}",
                )
            )
            continue
        try:
            ruleset = load_ruleset(entry.path)
        except RuleSetValidationError as exc:
            results.append(
                GateResult(
                    gate_name=f"rules.load.{entry.short_name}",
                    verdict=Verdict.FAIL,
                    notes=str(exc),
                )
            )
            continue
        report = coverage_gate_features(
            parsed, ruleset, ruleset_short_name=entry.short_name
        )
        gr = report.gate_result
        results.append(
            GateResult(
                gate_name=gate_name,
                verdict=gr.verdict,
                findings=gr.findings,
                notes=gr.notes,
                traces=gr.traces,
            )
        )
    return results
```

## Callee: pickled_rules.gates_runner._workdir_config (hop 1)

```python
def _workdir_config(root: Path) -> dict[str, Any]:
    cfg_path = root / "pickled.ruleset.yaml"
    if not cfg_path.is_file():
        return {}
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}
```

## Callee: pickled_rules.gates_runner._resolve_ruleset_entries (hop 1)

```python
def _resolve_ruleset_entries(root: Path, cfg: dict[str, Any]) -> list[_RulesetEntry]:
    has_singular = "ruleset" in cfg
    has_plural = "rulesets" in cfg
    if has_singular and has_plural:
        msg = (
            "pickled.ruleset.yaml: keys 'ruleset' and 'rulesets' are mutually exclusive"
        )
        raise RuleSetValidationError(msg)

    if has_singular:
        ruleset_rel = cfg.get("ruleset")
        if not isinstance(ruleset_rel, str):
            msg = "pickled.ruleset.yaml: 'ruleset' must be a string path"
            raise RuleSetValidationError(msg)
        path = (root / ruleset_rel).resolve()
        short_name = str(cfg.get("ruleset_short_name", path.stem))
        return [_RulesetEntry(path=path, short_name=short_name)]

    if has_plural:
        raw_list = cfg.get("rulesets")
        if not isinstance(raw_list, list):
            msg = "pickled.ruleset.yaml: 'rulesets' must be a list"
            raise RuleSetValidationError(msg)
        if not raw_list:
            msg = "pickled.ruleset.yaml: at least one ruleset entry required"
            raise RuleSetValidationError(msg)

        entries: list[_RulesetEntry] = []
        seen_short_names: dict[str, int] = {}
        for index, item in enumerate(raw_list):
            if not isinstance(item, dict):
                msg = f"pickled.ruleset.yaml: rulesets[{index}] must be a mapping"
                raise RuleSetValidationError(msg)
            path_raw = item.get("path")
            if not isinstance(path_raw, str):
                msg = f"pickled.ruleset.yaml: rulesets[{index}].path must be a string"
                raise RuleSetValidationError(msg)
            short_raw = item.get("short_name")
            if short_raw is not None and not isinstance(short_raw, str):
                msg = (
                    f"pickled.ruleset.yaml: rulesets[{index}].short_name must be a string"
                )
                raise RuleSetValidationError(msg)
            resolved = (root / path_raw).resolve()
            short_name = str(short_raw) if short_raw is not None else Path(path_raw).stem
            if short_name in seen_short_names:
                prior = seen_short_names[short_name]
                msg = (
                    f"duplicate short_name {short_name!r} at positions "
                    f"[{prior}, {index}]"
                )
                raise RuleSetValidationError(msg)
            seen_short_names[short_name] = index
            entries.append(_RulesetEntry(path=resolved, short_name=short_name))
        return entries

    return []
```

## Callee: pickled_rules.gates_runner._feature_glob (hop 1)

```python
def _feature_glob(cfg: dict[str, Any]) -> str:
    raw = cfg.get("feature_glob")
    if raw is None:
        return "features/**/*.feature"
    if not isinstance(raw, str):
        msg = "pickled.ruleset.yaml: 'feature_glob' must be a string"
        raise RuleSetValidationError(msg)
    return raw
```

## Callee: pickled_rules.gates.coverage.coverage_gate_features (hop 1)

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

## Callee: pickled_rules.loader.load_ruleset (hop 1)

```python
def load_ruleset(path: Path) -> RuleSet:
    """Load a rule set from YAML.

    Raises `RuleSetValidationError` on malformed input.
    """
    try:
        with path.open(encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise RuleSetValidationError(f"Malformed YAML in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise RuleSetValidationError(f"Rule set root must be a mapping, got {type(raw).__name__}")

    metadata_raw = _require(raw, "metadata", path)
    if not isinstance(metadata_raw, dict):
        raise RuleSetValidationError(
            f"`metadata` must be a mapping in {path}, got {type(metadata_raw).__name__}"
        )
    metadata = metadata_raw

    rules_raw = _require(raw, "rules", path)
    if not isinstance(rules_raw, list):
        raise RuleSetValidationError(f"`rules` must be a list in {path}")

    rules = tuple(_parse_rule(r, path) for r in rules_raw)

    source_url_raw = metadata.get("source_url")
    if source_url_raw is not None and not isinstance(source_url_raw, str):
        raise RuleSetValidationError(f"`source_url` must be a string or null in {path}")

    return RuleSet(
        source_id=_str_field(metadata, "source_id", path),
        source_title=_str_field(metadata, "source_title", path),
        applies_to=_str_field(metadata, "applies_to", path),
        maintainer=_str_field(metadata, "maintainer", path),
        source_version=_str_field(metadata, "source_version", path),
        active_from=_parse_date(_require(metadata, "active_from", path), path),
        source_url=source_url_raw,
        rules=rules,
    )
```

## Callee: pickled_rules.gates.coverage._collect_references (hop 2)

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

## Unresolved callees

- `adapter.parse_feature_file` — variable 'adapter' reassigned; type not stable
- `path.open` — method name matches multiple classes; receiver type not pinned

## Notes

Collection stopped early because of --max-callees or --max-code-lines.
