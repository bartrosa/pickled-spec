# Code context: parse

- **Surface id:** pickled_data_parse
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 6 | **Total lines:** 30 | **Truncated:** False

## Root: pickled_data.cli.parse

```python
def parse(migration: Path, dialect: str) -> None:
    """Parse a migration SQL file and print AST summary."""
    _check_dbt(migration)
    artifact = load_sql_file(migration, dialect=dialect)
    summary = ast_summary(artifact.ast)
    click.echo(json.dumps({"dialect": artifact.dialect, **summary}, indent=2))
```

## Callee: pickled_data.cli._check_dbt (hop 1)

```python
def _check_dbt(path: Path) -> None:
    if path.suffix == ".dbt":
        raise NotImplementedError(DBT_NOT_IMPLEMENTED_MSG)
```

## Callee: pickled_data.parser.load_sql_file (hop 1)

```python
def load_sql_file(path: Path, dialect: str = "postgres") -> SQLArtifact:
    _reject_dbt(path)
    content = path.read_text(encoding="utf-8")
    ast = parse_sql(content, dialect=dialect)
    return SQLArtifact(content=content, dialect=dialect, ast=ast)
```

## Callee: pickled_data.parser.ast_summary (hop 1)

```python
def ast_summary(ast: Any) -> dict[str, str]:
    """Short summary for CLI / MCP."""
    return {"kind": type(ast).__name__, "sql": ast.sql(dialect="postgres")}
```

## Callee: pickled_data.parser._reject_dbt (hop 2)

```python
def _reject_dbt(path: Path | None) -> None:
    if path is not None and path.suffix == ".dbt":
        raise NotImplementedError(DBT_NOT_IMPLEMENTED_MSG)
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
