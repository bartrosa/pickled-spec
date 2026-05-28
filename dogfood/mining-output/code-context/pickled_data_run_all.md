# Code context: run_all

- **Surface id:** pickled_data_run_all
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 4 | **Total lines:** 107 | **Truncated:** True

## Root: pickled_data.gates_runner.run_all

```python
def run_all(workdir: Path | str) -> list[GateResult]:
    """Parse migrations and run drift gate vs ``expected_schema.yaml``."""
    root = Path(workdir).resolve()
    migrations = sorted(root.glob("migrations/*.sql"))
    expected_path = root / "expected_schema.yaml"

    if not migrations:
        return [
            GateResult(
                gate_name="data.migrations",
                verdict=Verdict.WARN,
                notes="no migrations/*.sql",
            )
        ]

    results: list[GateResult] = []
    dialect = "sqlite"
    for mig in migrations:
        try:
            load_sql_file(mig, dialect=dialect)
        except SQLParseError as exc:
            results.append(
                GateResult(
                    gate_name=f"data.parse.{mig.name}",
                    verdict=Verdict.FAIL,
                    notes=str(exc),
                )
            )
        else:
            results.append(
                GateResult(
                    gate_name=f"data.parse.{mig.name}",
                    verdict=Verdict.PASS,
                    notes="parsed",
                )
            )

    if len(migrations) > 1:
        results.append(
            GateResult(
                gate_name="data.migrations.note",
                verdict=Verdict.WARN,
                notes=f"applying {len(migrations)} migrations in filename order for drift",
            )
        )

    if expected_path.is_file() and migrations:
        combined_sql = "\n\n".join(
            mig.read_text(encoding="utf-8") for mig in migrations
        )
        expected = yaml.safe_load(expected_path.read_text(encoding="utf-8"))
        if isinstance(expected, dict):
            gr = MigrationDriftGate().run(
                combined_sql,
                context={"expected_schema": expected, "dialect": dialect},
            )
            results.append(
                GateResult(
                    gate_name="data.migration_drift",
                    verdict=gr.verdict,
                    notes=gr.notes,
                )
            )
    return results
```

## Callee: pickled_data.parser.load_sql_file (hop 1)

```python
def load_sql_file(path: Path, dialect: str = "postgres") -> SQLArtifact:
    _reject_dbt(path)
    content = path.read_text(encoding="utf-8")
    ast = parse_sql(content, dialect=dialect)
    return SQLArtifact(content=content, dialect=dialect, ast=ast)
```

## Callee: pickled_data.MigrationDriftGate.run (hop 1)

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

## Callee: pickled_data.parser._reject_dbt (hop 2)

```python
def _reject_dbt(path: Path | None) -> None:
    if path is not None and path.suffix == ".dbt":
        raise NotImplementedError(DBT_NOT_IMPLEMENTED_MSG)
```

## Notes

Collection stopped early because of --max-callees or --max-code-lines.
