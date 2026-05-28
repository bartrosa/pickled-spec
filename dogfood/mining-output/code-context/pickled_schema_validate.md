# Code context: validate

- **Surface id:** pickled_schema_validate
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 4 | **Total lines:** 57 | **Truncated:** True

## Root: pickled_schema.cli.validate

```python
def validate(file: Path) -> None:
    """Validate a schema file against its format specification."""
    fmt = _infer_format(file)
    if fmt in (
        SchemaFormat.openapi_3_0,
        SchemaFormat.openapi_3_1,
        SchemaFormat.openapi_3_2,
    ):
        spec_dict, _, _ = load_openapi_file(file)
        validate_openapi_dict(spec_dict)
    elif fmt is SchemaFormat.json_schema_2020_12:
        schema_dict, _ = load_json_schema_file(file)
        validate_json_schema_document(schema_dict)
    elif fmt is SchemaFormat.proto3:
        parse_proto_file(file)
    click.echo(json.dumps({"valid": True, "format": fmt.value}))
```

## Callee: pickled_schema.cli._infer_format (hop 1)

```python
def _infer_format(path: Path) -> SchemaFormat:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return SchemaFormat.openapi_3_1
    if suffix == ".json":
        return SchemaFormat.json_schema_2020_12
    if suffix == ".proto":
        return SchemaFormat.proto3
    msg = f"cannot infer format from extension {suffix!r}; use --format"
    raise click.ClickException(msg)
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

## Notes

Collection stopped early because of --max-callees or --max-code-lines.
