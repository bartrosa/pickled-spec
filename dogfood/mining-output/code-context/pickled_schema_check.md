# Code context: check

- **Surface id:** pickled_schema_check
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 7 | **Total lines:** 150 | **Truncated:** False

## Root: pickled_schema.cli.check

```python
def check(spec: Path, feature_dir: Path | None, feature_glob: str | None) -> None:
    """Run SchemaCoverageGate on @schema:endpoint tags in .feature files."""
    spec_dict, _, _ = load_openapi_file(spec)
    feature_paths = _resolve_feature_paths(feature_dir, feature_glob)
    if not feature_paths:
        raise click.ClickException("No feature files matched")
    gate = SchemaCoverageGate()
    result = gate.run(spec_dict, context={"feature_paths": feature_paths})
    payload = {
        "gate": result.gate_name,
        "verdict": result.verdict.value,
        "notes": result.notes,
        "findings": [
            {"tag": f.tag, "source": f.source}
            for f in result.findings
            if isinstance(f, SchemaCoverageFinding)
        ],
    }
    click.echo(json.dumps(payload, indent=2))
    if result.verdict is Verdict.FAIL:
        raise SystemExit(2)
    if result.verdict is Verdict.WARN:
        raise SystemExit(1)
```

## Callee: pickled_schema.openapi.parser.load_openapi_file (hop 1)

```python
def load_openapi_file(path: Path) -> tuple[dict[str, Any], SchemaFormat, SchemaArtifact]:
    """Load a file and return parsed dict, detected format, and artifact."""
    data, raw = _load_text(path)
    fmt = detect_format(data)
    artifact = SchemaArtifact(
        format=fmt,
        content=raw,
        endpoint_id=None,
        source="file",
    )
    return data, fmt, artifact
```

## Callee: pickled_schema.cli._resolve_feature_paths (hop 1)

```python
def _resolve_feature_paths(
    feature_dir: Path | None,
    feature_glob: str | None,
) -> list[Path]:
    if feature_dir is not None and feature_glob is not None:
        raise click.ClickException("Use only one of --feature-dir or --feature-glob")
    if feature_dir is not None:
        return sorted(feature_dir.glob("**/*.feature"))
    if feature_glob is not None:
        from glob import glob

        return sorted(Path(p) for p in glob(feature_glob, recursive=True) if Path(p).is_file())
    raise click.ClickException("Provide --feature-dir or --feature-glob")
```

## Callee: pickled_schema.SchemaCoverageGate.run (hop 1)

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

## Callee: pickled_schema.openapi.parser._load_text (hop 2)

```python
def _load_text(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(raw)
    elif suffix == ".json":
        data = json.loads(raw)
    else:
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            msg = f"cannot parse {path}: not valid YAML or JSON"
            raise SchemaParseError(msg) from exc
    if not isinstance(data, dict):
        msg = "schema root must be a mapping"
        raise SchemaParseError(msg)
    return data, raw
```

## Callee: pickled_schema.openapi.parser.detect_format (hop 2)

```python
def detect_format(spec_dict: dict[str, Any]) -> SchemaFormat:
    """Infer OpenAPI version from a parsed document root."""
    if "swagger" in spec_dict:
        msg = "OpenAPI 2.0 (swagger field) is not supported in v0.1"
        raise SchemaParseError(msg)
    version = spec_dict.get("openapi")
    if not isinstance(version, str):
        msg = "missing or invalid top-level 'openapi' version field"
        raise SchemaParseError(msg)
    if version.startswith("3.2"):
        return SchemaFormat.openapi_3_2
    if version.startswith("3.1"):
        return SchemaFormat.openapi_3_1
    if version.startswith("3.0"):
        return SchemaFormat.openapi_3_0
    msg = f"unsupported OpenAPI version {version!r}"
    raise SchemaParseError(msg)
```

## Callee: pickled_schema._missing_tags (hop 2)

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
