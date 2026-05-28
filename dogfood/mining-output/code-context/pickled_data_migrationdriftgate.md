# Code context: MigrationDriftGate.run

- **Surface id:** pickled_data_migrationdriftgate
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 5 | **Total lines:** 132 | **Truncated:** True

## Root: pickled_data.gates.MigrationDriftGate.run

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
                notes=f"Expected migration SQL string, got {type(target).__name__}",
            )
        expected = ctx.get("expected_schema")
        if not isinstance(expected, dict):
            raw = ctx.get("expected_schema_yaml")
            if isinstance(raw, str):
                loaded = yaml.safe_load(raw)
                expected = loaded if isinstance(loaded, dict) else None
        if not isinstance(expected, dict):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes='context needs "expected_schema" or "expected_schema_yaml"',
            )
        dialect = str(ctx.get("dialect", "postgres"))
        actual = apply_migration(target, dialect=dialect)
        exp_tables = _normalize_columns(expected)
        act_tables = _normalize_columns(actual)
        ok, notes = _compare_schemas(exp_tables, act_tables)
        return GateResult(
            gate_name=self.name,
            verdict=Verdict.PASS if ok else Verdict.FAIL,
            notes=notes,
        )
```

## Callee: pickled_data.oracle.apply_migration (hop 1)

```python
def apply_migration(
    sql: str,
    target_db: Path | None = None,
    *,
    dialect: str = "postgres",
) -> dict[str, Any]:
    """Apply DDL/DML and return resulting schema summary."""
    parse_sql(sql, dialect=dialect)
    statements = sqlglot.parse(sql, dialect=dialect)
    _reject_filesystem_escapes(statements)
    sqlite_sqls: list[str] = []
    for stmt in statements:
        if stmt is None:
            continue
        transpiled = stmt.sql(dialect="sqlite")
        if transpiled.strip():
            sqlite_sqls.append(transpiled)

    conn = (
        sqlite3.connect(str(target_db))
        if target_db is not None
        else sqlite3.connect(":memory:")
    )

    try:
        # Defense in depth: even if a future transpilation quirk reintroduces
        # an ATTACH statement past the AST check, SQLite refuses to attach
        # anything when SQLITE_LIMIT_ATTACHED == 0.
        try:
            conn.setlimit(sqlite3.SQLITE_LIMIT_ATTACHED, 0)
        except AttributeError:  # pragma: no cover — only Python <3.11
            pass
        for statement in sqlite_sqls:
            conn.execute(statement)
        conn.commit()
        return _introspect(conn)
    finally:
        conn.close()
```

## Callee: pickled_data.gates._normalize_columns (hop 1)

```python
def _normalize_columns(schema: dict[str, Any]) -> dict[str, set[tuple[str, str, bool]]]:
    """Map table name -> set of (name, type, nullable)."""
    out: dict[str, set[tuple[str, str, bool]]] = {}
    for table in schema.get("tables", []):
        if not isinstance(table, dict):
            continue
        name = str(table.get("name", ""))
        cols: set[tuple[str, str, bool]] = set()
        for col in table.get("columns", []):
            if isinstance(col, dict):
                cols.add(
                    (
                        str(col.get("name", "")),
                        str(col.get("type", "TEXT")).upper(),
                        bool(col.get("nullable", True)),
                    )
                )
        out[name] = cols
    return out
```

## Callee: pickled_data.gates._compare_schemas (hop 1)

```python
def _compare_schemas(
    expected: dict[str, set[tuple[str, str, bool]]],
    actual: dict[str, set[tuple[str, str, bool]]],
) -> tuple[bool, str]:
    """Compare schemas; ignore nullable-only drift (e.g. SQLite DEFAULT → NOT NULL)."""
    if set(expected) != set(actual):
        return (
            False,
            f"drift: expected tables {sorted(expected)} vs actual {sorted(actual)}",
        )
    nullable_notes: list[str] = []
    for table in sorted(expected):
        exp_cols = expected[table]
        act_cols = actual[table]
        if _column_keys(exp_cols) != _column_keys(act_cols):
            return (
                False,
                f"drift: table {table!r} expected {_column_keys(exp_cols)} "
                f"vs actual {_column_keys(act_cols)}",
            )
        exp_null = {(n, t): nullable for n, t, nullable in exp_cols}
        act_null = {(n, t): nullable for n, t, nullable in act_cols}
        for key, exp_n in exp_null.items():
            act_n = act_null.get(key)
            if act_n is not None and exp_n != act_n:
                nullable_notes.append(f"{table}.{key[0]} expected nullable={exp_n} got {act_n}")
    if nullable_notes:
        detail = "; ".join(nullable_notes)
        return True, f"Schema matches expected (nullable differs: {detail})."
    return True, "Schema matches expected."
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

- `sqlglot.parse` — method name matches multiple classes; receiver type not pinned
- `stmt.sql` — method name matches multiple classes; receiver type not pinned
- `conn.commit` — variable 'conn' reassigned; type not stable
- `conn.close` — variable 'conn' reassigned; type not stable
- `conn.setlimit` — variable 'conn' reassigned; type not stable
- `conn.execute` — variable 'conn' reassigned; type not stable
- `cols.add` — method name matches multiple classes; receiver type not pinned

## Notes

Collection stopped early because of --max-callees or --max-code-lines.
