# Code context: apply

- **Surface id:** pickled_data_apply
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 6 | **Total lines:** 90 | **Truncated:** False

## Root: pickled_data.cli.apply

```python
def apply(migration: Path, dialect: str) -> None:
    """Apply migration to in-memory SQLite and print resulting schema."""
    _check_dbt(migration)
    sql = migration.read_text(encoding="utf-8")
    schema = apply_migration(sql, dialect=dialect)
    click.echo(json.dumps(schema, indent=2))
```

## Callee: pickled_data.cli._check_dbt (hop 1)

```python
def _check_dbt(path: Path) -> None:
    if path.suffix == ".dbt":
        raise NotImplementedError(DBT_NOT_IMPLEMENTED_MSG)
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

## Callee: pickled_data.oracle._reject_filesystem_escapes (hop 2)

```python
def _reject_filesystem_escapes(statements: list[exp.Expression | None]) -> None:
    """Refuse ATTACH/DETACH statements before any SQL is executed."""
    for stmt in statements:
        if stmt is None:
            continue
        if isinstance(stmt, exp.Attach | exp.Detach):
            raise UnsafeMigrationStatementError(
                f"ATTACH/DETACH statements are not allowed in the sandbox: "
                f"{stmt.sql(dialect='sqlite')!r}"
            )
        for node in stmt.find_all(exp.Attach, exp.Detach):
            raise UnsafeMigrationStatementError(
                f"ATTACH/DETACH statements are not allowed in the sandbox: "
                f"{node.sql(dialect='sqlite')!r}"
            )
```

## Callee: pickled_data.oracle._introspect (hop 2)

```python
def _introspect(conn: sqlite3.Connection) -> dict[str, Any]:
    tables: list[dict[str, Any]] = []
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    for (name,) in cur.fetchall():
        cols: list[dict[str, Any]] = []
        info = conn.execute(f"PRAGMA table_info({name})").fetchall()
        for _cid, col_name, col_type, notnull, _default, _pk in info:
            cols.append(
                {
                    "name": col_name,
                    "type": (col_type or "TEXT").upper(),
                    "nullable": not bool(notnull),
                }
            )
        tables.append({"name": name, "columns": cols})
    return {"tables": tables}
```

## Unresolved callees

- `sqlglot.parse` — method name matches multiple classes; receiver type not pinned
- `stmt.sql` — method name matches multiple classes; receiver type not pinned
- `conn.commit` — variable 'conn' reassigned; type not stable
- `conn.close` — variable 'conn' reassigned; type not stable
- `conn.setlimit` — variable 'conn' reassigned; type not stable
- `conn.execute` — variable 'conn' reassigned; type not stable
