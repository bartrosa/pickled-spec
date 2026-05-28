# Code context: DataContractGate.run

- **Surface id:** pickled_data_datacontractgate
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 4 | **Total lines:** 110 | **Truncated:** False

## Root: pickled_data.gates.DataContractGate.run

```python
def run(
        self,
        target: object,
        *,
        context: dict[str, Any] | None = None,
    ) -> GateResult:
        ctx = context or {}
        if not isinstance(target, str):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected SQL string, got {type(target).__name__}",
            )
        endpoint_tag = ctx.get("endpoint_tag")
        if not isinstance(endpoint_tag, str):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes='context must contain "endpoint_tag"',
            )
        if self._registry is None:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                notes="no SchemaRegistry configured",
            )
        artifact = self._registry.find_schema_by_tag(endpoint_tag)
        if artifact is None:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                notes=f"no schema for tag {endpoint_tag!r}",
            )
        sql_columns = _select_column_names(target)
        api_columns = _openapi_response_property_names(artifact.content)
        if not api_columns:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                notes="could not extract OpenAPI response properties",
            )
        api_set = set(api_columns)
        sql_set = set(sql_columns)
        missing = sorted(sql_set - api_set)
        extra = sorted(api_set - sql_set)
        if missing or extra:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"column mismatch missing={missing} extra={extra}",
            )
        return GateResult(
            gate_name=self.name,
            verdict=Verdict.PASS,
            notes="column names match OpenAPI properties (types not checked in v0.1)",
        )
```

## Callee: pickled_data.gates._select_column_names (hop 1)

```python
def _select_column_names(sql: str) -> list[str]:
    """Extract output column names from a SELECT (best-effort)."""
    try:
        ast = parse_sql(sql, dialect="postgres")
    except Exception:
        return []
    cols: list[str] = []
    for node in ast.find_all(exp.Select):
        for expr in node.expressions:
            alias = getattr(expr, "alias", None)
            if alias:
                cols.append(str(alias))
            elif hasattr(expr, "name") and expr.name:
                cols.append(str(expr.name))
    return cols
```

## Callee: pickled_data.gates._openapi_response_property_names (hop 1)

```python
def _openapi_response_property_names(spec_yaml: str) -> list[str]:
    import yaml

    try:
        spec = yaml.safe_load(spec_yaml)
    except yaml.YAMLError:
        return []
    if not isinstance(spec, dict):
        return []
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        return []
    for _path, item in paths.items():
        if not isinstance(item, dict):
            continue
        for _method, op in item.items():
            if not isinstance(op, dict):
                continue
            responses = op.get("responses") or {}
            ok = responses.get("200") or responses.get("201")
            if not isinstance(ok, dict):
                continue
            content = ok.get("content") or {}
            app_json = content.get("application/json") or {}
            schema = app_json.get("schema") or {}
            props = schema.get("properties") or {}
            if isinstance(props, dict):
                return sorted(str(k) for k in props)
    return []
```

## Callee: pickled_data.parser.parse_sql (hop 2)

```python
def parse_sql(sql: str, dialect: str = "postgres") -> exp.Expr:
    """Parse SQL into a sqlglot AST."""
    try:
        parsed = sqlglot.parse_one(sql, dialect=dialect)
    except sqlglot.errors.ParseError as exc:
        raise SQLParseError(str(exc)) from exc
    if parsed is None:
        msg = "empty parse result"
        raise SQLParseError(msg)
    return parsed
```

## Unresolved callees

- `self._registry.find_schema_by_tag` — protocol or unknown attribute type
- `getattr(expr, 'alias', None)` — dynamic attribute access
