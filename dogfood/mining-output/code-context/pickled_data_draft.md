# Code context: draft

- **Surface id:** pickled_data_draft
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 8 | **Total lines:** 120 | **Truncated:** False

## Root: pickled_data.cli.draft

```python
def draft(
    intent: str,
    dialect: str,
    current_schema: Path | None,
    output: Path | None,
) -> None:
    """Draft a SQL migration from a natural-language intent."""
    schema_yaml: str | None = None
    if current_schema is not None:
        schema_yaml = current_schema.read_text(encoding="utf-8")
    try:
        llm = _build_llm_client()
        result = MigrationDrafter(llm).draft_from_intent(
            intent_text=_read_text_arg(intent),
            dialect=dialect,
            current_schema_yaml=schema_yaml,
        )
    except click.ClickException:
        raise
    except Exception as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(2) from exc
    _emit_draft_output(
        text=result.text,
        rationale=result.rationale,
        warnings=result.warnings,
        output=output,
    )
```

## Callee: pickled_data.cli._build_llm_client (hop 1)

```python
def _build_llm_client() -> LLMClient:
    from pickled_core.llm.bootstrap import build_default_client
    from pickled_core.llm.config import ConfigError

    try:
        return build_default_client(factory_env="PICKLED_DATA_LLM_FACTORY")
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc
```

## Callee: pickled_data.MigrationDrafter.draft_from_intent (hop 1)

```python
def draft_from_intent(
        self,
        *,
        intent_text: str,
        dialect: str,
        current_schema_yaml: str | None = None,
    ) -> DraftResult:
        prompt = self._build_prompt(
            intent_text=intent_text,
            dialect=dialect,
            current_schema_yaml=current_schema_yaml,
        )
        completion = self._llm.complete(
            messages=[Message(role="user", content=prompt)],
            model=_DRAFT_MODEL,
            max_tokens=4000,
            temperature=0.0,
            stop=None,
            extras=None,
        )
        text, rationale = self._split_output(completion.text)
        warnings = tuple(self._validate(text, dialect=dialect))
        return DraftResult(text=text, rationale=rationale, warnings=warnings)
```

## Callee: pickled_data.cli._read_text_arg (hop 1)

```python
def _read_text_arg(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")
```

## Callee: pickled_data.cli._emit_draft_output (hop 1)

```python
def _emit_draft_output(
    *,
    text: str,
    rationale: str,
    warnings: tuple[str, ...],
    output: Path | None,
) -> None:
    if output is not None:
        output.write_text(text, encoding="utf-8")
    else:
        click.echo(text)
    if rationale:
        for line in rationale.splitlines():
            click.echo(f"rationale: {line}", err=True)
    for warning in warnings:
        click.echo(f"warning: {warning}", err=True)
    if warnings:
        raise SystemExit(1)
```

## Callee: pickled_data.MigrationDrafter._build_prompt (hop 2)

```python
def _build_prompt(
        self,
        *,
        intent_text: str,
        dialect: str,
        current_schema_yaml: str | None,
    ) -> str:
        schema_block = current_schema_yaml.strip() if current_schema_yaml else "none"
        return (
            "You are drafting a SQL migration for the pickled-data tool. Given:\n\n"
            f"- dialect: {dialect}\n"
            f"- intent: {intent_text.strip()}\n"
            f"- current schema (optional YAML): {schema_block}\n\n"
            "Emit a single SQL migration file. Use only DDL statements valid in "
            "the stated dialect. Begin with a comment line "
            "`-- intent: <one-line summary>`. "
            "Do NOT include destructive operations (DROP DATABASE, TRUNCATE entire "
            "tables without a WHERE clause is N/A for DDL). "
            f"After the SQL, emit the literal line {RATIONALE_SENTINEL!r} then "
            "1-3 sentences explaining choices."
        )
```

## Callee: pickled_data.MigrationDrafter._split_output (hop 2)

```python
def _split_output(self, raw: str) -> tuple[str, str]:
        if RATIONALE_SENTINEL in raw:
            text, _, rationale = raw.partition(RATIONALE_SENTINEL)
            return text.strip(), rationale.strip()
        return raw.strip(), ""
```

## Callee: pickled_data.MigrationDrafter._validate (hop 2)

```python
def _validate(self, text: str, *, dialect: str) -> list[str]:
        warnings: list[str] = []
        try:
            sqlglot.parse(text, dialect=dialect)
        except Exception as exc:  # noqa: BLE001 — surface any parse failure
            warnings.append(str(exc))
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "drop table" in line.lower():
                warnings.append(
                    f"destructive operation on line {line_no} "
                    f"('DROP TABLE'); confirm intent before applying"
                )
        return warnings
```

## Unresolved callees

- `self._llm.complete` — protocol or unknown attribute type
- `sys.stdin.read` — method name matches multiple classes; receiver type not pinned
- `rationale.splitlines` — method name matches multiple classes; receiver type not pinned
