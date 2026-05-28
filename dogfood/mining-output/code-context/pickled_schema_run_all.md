# Code context: run_all

- **Surface id:** pickled_schema_run_all
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 5 | **Total lines:** 135 | **Truncated:** False

## Root: pickled_schema.gates_runner.run_all

```python
def run_all(workdir: Path | str) -> list[GateResult]:
    """Validate OpenAPI under ``specs/`` and run schema coverage on features."""
    root = Path(workdir).resolve()
    results: list[GateResult] = []

    spec_candidates = sorted(root.glob("specs/*.yaml")) + sorted(
        root.glob("specs/*.yml")
    )
    if not spec_candidates:
        results.append(
            GateResult(
                gate_name="schema.openapi",
                verdict=Verdict.WARN,
                notes="no specs/*.yaml",
            )
        )
        return results

    valid_specs: list[tuple[Path, dict]] = []
    for spec_path in spec_candidates:
        try:
            spec_dict, _, _ = load_openapi_file(spec_path)
            validate_openapi_dict(spec_dict)
        except (SchemaValidationError, OSError, ValueError, TypeError) as exc:
            results.append(
                GateResult(
                    gate_name=f"schema.openapi.validate.{spec_path.name}",
                    verdict=Verdict.FAIL,
                    notes=str(exc),
                )
            )
        else:
            valid_specs.append((spec_path, spec_dict))
            results.append(
                GateResult(
                    gate_name=f"schema.openapi.validate.{spec_path.name}",
                    verdict=Verdict.PASS,
                    notes=str(spec_path.relative_to(root)),
                )
            )

    if not valid_specs:
        return results

    if len(valid_specs) > 1:
        results.append(
            GateResult(
                gate_name="schema.openapi.note",
                verdict=Verdict.WARN,
                notes=(
                    f"{len(valid_specs)} OpenAPI files under specs/; "
                    f"coverage uses {valid_specs[0][0].name}"
                ),
            )
        )

    spec_path, spec_dict = valid_specs[0]
    feature_paths = sorted(root.glob("features/**/*.feature"))
    if feature_paths:
        gate = SchemaCoverageGate()
        gr = gate.run(spec_dict, context={"feature_paths": feature_paths})
        results.append(
            GateResult(
                gate_name="schema.coverage",
                verdict=gr.verdict,
                findings=gr.findings,
                notes=gr.notes or str(spec_path.relative_to(root)),
            )
        )
    return results
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

## Callee: pickled_schema.openapi.validator.validate_openapi_dict (hop 1)

```python
def validate_openapi_dict(spec_dict: dict[str, Any]) -> None:
    """Validate *spec_dict* with openapi-spec-validator."""
    try:
        from openapi_spec_validator import validate
        from openapi_spec_validator.exceptions import OpenAPIError
        from openapi_spec_validator.validation.exceptions import (
            OpenAPIValidationError,
        )
    except ImportError as exc:
        msg = "install pickled-schema[openapi] for OpenAPI validation"
        raise SchemaValidationError(msg) from exc

    try:
        validate(spec_dict)
    except (OpenAPIError, OpenAPIValidationError) as exc:
        errors = [str(exc)]
        nested = getattr(exc, "schema_errors", None)
        if nested:
            errors.extend(str(e) for e in nested)
        raise SchemaValidationError("OpenAPI validation failed", errors=errors) from exc
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

## Unresolved callees

- `spec_path.relative_to` — method name matches multiple classes; receiver type not pinned
- `gate.run` — method name matches multiple classes; receiver type not pinned
- `getattr(exc, 'schema_errors', None)` — dynamic attribute access
