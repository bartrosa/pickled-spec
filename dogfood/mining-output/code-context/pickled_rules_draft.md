# Code context: draft

- **Surface id:** pickled_rules_draft
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 8 | **Total lines:** 141 | **Truncated:** False

## Root: pickled_rules.cli.draft

```python
def draft(
    brief: str,
    short_name: str,
    source_id: str,
    applies_to: str,
    active_from: str,
    output: Path | None,
) -> None:
    """Draft a YAML rule set from a natural-language brief."""
    try:
        llm = _build_llm_client()
        result = RuleSetDrafter(llm).draft_from_brief(
            brief_text=_read_text_arg(brief),
            ruleset_short_name=short_name,
            source_id=source_id,
            applies_to=applies_to,
            active_from=active_from,
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

## Callee: pickled_rules.cli._build_llm_client (hop 1)

```python
def _build_llm_client() -> LLMClient:
    from pickled_core.llm.bootstrap import build_default_client
    from pickled_core.llm.config import ConfigError

    try:
        return build_default_client(factory_env="PICKLED_RULES_LLM_FACTORY")
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc
```

## Callee: pickled_rules.RuleSetDrafter.draft_from_brief (hop 1)

```python
def draft_from_brief(
        self,
        *,
        brief_text: str,
        ruleset_short_name: str,
        source_id: str,
        applies_to: str,
        active_from: str,
    ) -> DraftResult:
        prompt = self._build_prompt(
            brief_text=brief_text,
            ruleset_short_name=ruleset_short_name,
            source_id=source_id,
            applies_to=applies_to,
            active_from=active_from,
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
        warnings = tuple(self._validate(text))
        return DraftResult(text=text, rationale=rationale, warnings=warnings)
```

## Callee: pickled_rules.cli._read_text_arg (hop 1)

```python
def _read_text_arg(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")
```

## Callee: pickled_rules.cli._emit_draft_output (hop 1)

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

## Callee: pickled_rules.RuleSetDrafter._build_prompt (hop 2)

```python
def _build_prompt(
        self,
        *,
        brief_text: str,
        ruleset_short_name: str,
        source_id: str,
        applies_to: str,
        active_from: str,
    ) -> str:
        banned = ", ".join(sorted(_FORBIDDEN_TOKENS))
        return (
            "You are drafting a YAML rule set for the pickled-rules tool. "
            "The input is a natural-language brief describing a domain. "
            "Emit YAML matching this schema exactly:\n\n"
            "```yaml\n"
            "metadata:\n"
            f'  source_id: "{source_id}"\n'
            '  source_title: "<concise>"\n'
            f'  applies_to: "{applies_to}"\n'
            '  maintainer: "drafted by LLM"\n'
            '  source_version: "0.1"\n'
            f'  active_from: "{active_from}"\n'
            "rules:\n"
            '  - id: "<unique kebab-case>"\n'
            '    title: "<5-10 words>"\n'
            '    description: "<one paragraph>"\n'
            '    enforcement: "strict" | "advisory" | "informational"\n'
            "```\n\n"
            f"Ruleset short name (for tagging): {ruleset_short_name}\n\n"
            "Brief:\n"
            f"{brief_text.strip()}\n\n"
            "Rules MUST use neutral, vendor-agnostic phrasing. "
            f"Do NOT include any of these tokens (case-insensitive): {banned}. "
            "Domain-specific terms belong only inside description: fields.\n\n"
            f"After the YAML, emit the literal line {RATIONALE_SENTINEL!r} then "
            "1-3 sentences explaining your rule selection."
        )
```

## Callee: pickled_rules.RuleSetDrafter._split_output (hop 2)

```python
def _split_output(self, raw: str) -> tuple[str, str]:
        if RATIONALE_SENTINEL in raw:
            text, _, rationale = raw.partition(RATIONALE_SENTINEL)
            return text.strip(), rationale.strip()
        return raw.strip(), ""
```

## Callee: pickled_rules.RuleSetDrafter._validate (hop 2)

```python
def _validate(self, text: str) -> list[str]:
        warnings: list[str] = []
        try:
            load_ruleset_from_text(text)
        except RuleSetValidationError as exc:
            warnings.append(str(exc))
        lowered = text.lower()
        for token in sorted(_FORBIDDEN_TOKENS):
            if token in lowered:
                warnings.append(
                    f"forbidden token '{token}' in YAML; rewrite the rule"
                )
        return warnings
```

## Unresolved callees

- `self._llm.complete` — protocol or unknown attribute type
- `sys.stdin.read` — method name matches multiple classes; receiver type not pinned
- `rationale.splitlines` — method name matches multiple classes; receiver type not pinned
