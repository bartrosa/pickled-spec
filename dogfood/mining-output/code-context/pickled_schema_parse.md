# Code context: parse

- **Surface id:** pickled_schema_parse
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 6 | **Total lines:** 101 | **Truncated:** False

## Root: pickled_schema.cli.parse

```python
def parse(file: Path, fmt: str | None) -> None:
    """Parse a schema file and print a short summary."""
    format_enum = SchemaFormat(fmt) if fmt else _infer_format(file)
    artifact = _load_artifact(file, format_enum)
    click.echo(
        json.dumps(
            {
                "format": artifact.format.value,
                "endpoint_id": artifact.endpoint_id,
                "source": artifact.source,
                "content_bytes": len(artifact.content.encode("utf-8")),
            },
            indent=2,
        )
    )
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

## Callee: pickled_schema.cli._load_artifact (hop 1)

```python
def _load_artifact(path: Path, fmt: SchemaFormat) -> SchemaArtifact:
    if fmt in (
        SchemaFormat.openapi_3_0,
        SchemaFormat.openapi_3_1,
        SchemaFormat.openapi_3_2,
    ):
        _, detected, artifact = load_openapi_file(path)
        return SchemaArtifact(
            format=detected,
            content=artifact.content,
            endpoint_id=artifact.endpoint_id,
            source=artifact.source,
        )
    if fmt is SchemaFormat.json_schema_2020_12:
        _, artifact = load_json_schema_file(path)
        return artifact
    if fmt is SchemaFormat.proto3:
        return parse_proto_file(path)
    raise click.ClickException(f"unsupported format {fmt!r}")
```

## Callee: pickled_schema.openapi.parser.load_openapi_file (hop 2)

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

## Callee: pickled_schema.json_schema.parser.load_json_schema_file (hop 2)

```python
def load_json_schema_file(path: Path) -> tuple[dict[str, Any], SchemaArtifact]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        msg = "JSON Schema root must be an object"
        raise SchemaParseError(msg)
    artifact = SchemaArtifact(
        format=SchemaFormat.json_schema_2020_12,
        content=raw,
        endpoint_id=None,
        source="file",
    )
    return data, artifact
```

## Callee: pickled_schema.proto.parser.parse_proto_file (hop 2)

```python
def parse_proto_file(
    proto_path: Path,
    proto_dir: Path | None = None,
) -> SchemaArtifact:
    """Parse a .proto file and return a descriptor set as base64 text."""
    pd = proto_dir or proto_path.parent
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "descriptor.bin"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "grpc_tools.protoc",
                f"--proto_path={pd}",
                f"--descriptor_set_out={out}",
                "--include_imports",
                str(proto_path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "protoc failed").strip()
            msg = f"protoc failed: {err}"
            raise RuntimeError(msg)
        data = out.read_bytes()
    return SchemaArtifact(
        format=SchemaFormat.proto3,
        content=base64.b64encode(data).decode("ascii"),
        endpoint_id=None,
        source="file",
    )
```
