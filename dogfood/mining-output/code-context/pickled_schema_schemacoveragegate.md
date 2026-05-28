# Code context: SchemaCoverageGate.run

- **Surface id:** pickled_schema_schemacoveragegate
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 3 | **Total lines:** 77 | **Truncated:** False

## Root: pickled_schema.gates.SchemaCoverageGate.run

```python
def run(
        self,
        target: object,
        *,
        context: dict[str, Any] | None = None,
    ) -> GateResult:
        ctx = context or {}
        if not isinstance(target, dict):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected parsed OpenAPI dict, got {type(target).__name__}",
            )

        feature_paths: list[Path] = []
        raw_paths = ctx.get("feature_paths")
        if isinstance(raw_paths, list):
            feature_paths = [Path(p) for p in raw_paths]

        feature_texts: list[tuple[str, str]] = []
        raw_texts = ctx.get("feature_texts")
        if isinstance(raw_texts, list):
            for i, text in enumerate(raw_texts):
                if isinstance(text, str):
                    feature_texts.append((f"<feature-{i}>", text))

        if not feature_paths and not feature_texts:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes='context needs "feature_paths" and/or "feature_texts"',
            )

        missing: list[SchemaCoverageFinding] = []
        for path in feature_paths:
            text = path.read_text(encoding="utf-8")
            missing.extend(
                _missing_tags(target, text, source=str(path)),
            )
        for source, text in feature_texts:
            missing.extend(_missing_tags(target, text, source=source))

        if not missing:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.PASS,
                notes="All @schema:endpoint tags have matching paths.",
            )

        lines = [f"{f.tag} ({f.source})" for f in missing]
        return GateResult(
            gate_name=self.name,
            verdict=Verdict.FAIL,
            findings=tuple(missing),
            notes="Missing endpoints: " + "; ".join(lines),
        )
```

## Callee: pickled_schema.gates._missing_tags (hop 1)

```python
def _missing_tags(
    spec: dict[str, Any],
    feature_text: str,
    *,
    source: str,
) -> list[SchemaCoverageFinding]:
    out: list[SchemaCoverageFinding] = []
    for match in _ENDPOINT_TAG_RE.finditer(feature_text):
        method, path = match.group(1), match.group(2)
        tag = match.group(0)
        if not _spec_has_endpoint(spec, method, path):
            out.append(SchemaCoverageFinding(tag=tag, source=source))
    return out
```

## Callee: pickled_schema.gates._spec_has_endpoint (hop 2)

```python
def _spec_has_endpoint(spec: dict[str, Any], method: str, path: str) -> bool:
    paths = spec.get("paths")
    if not isinstance(paths, dict) or path not in paths:
        return False
    item = paths[path]
    if not isinstance(item, dict):
        return False
    return method.lower() in item
```

## Unresolved callees

- `_ENDPOINT_TAG_RE.finditer` — method name matches multiple classes; receiver type not pinned
- `match.group` — method name matches multiple classes; receiver type not pinned
