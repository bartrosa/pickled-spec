# Code context: check

- **Surface id:** pickled_rules_check
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 2 | **Total lines:** 86 | **Truncated:** True

## Root: pickled_rules.cli.check

```python
def check(
    ruleset: str,
    feature_path: Path | None,
    feature_glob: str | None,
    ruleset_name: str | None,
    output_format: str,
    output: Path | None,
    quiet: bool,
) -> None:
    """Check feature coverage against a YAML rule set."""
    if feature_path is None and feature_glob is None:
        raise click.ClickException("Provide --feature or --feature-glob")
    if feature_path is not None and feature_glob is not None:
        raise click.ClickException("Use only one of --feature or --feature-glob")

    try:
        resolved_path = _resolve_ruleset_path(ruleset)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    if ruleset_name is not None:
        short_name = ruleset_name.lower()
    elif ruleset in BUILTIN_RULESETS:
        short_name = ruleset.lower()
    else:
        short_name = resolved_path.stem.lower()

    ruleset_obj = load_ruleset(resolved_path)
    if feature_glob:
        from glob import glob

        paths = [Path(p) for p in glob(feature_glob, recursive=True)]
        paths = [p for p in paths if p.is_file()]
    else:
        assert feature_path is not None
        paths = [feature_path]

    if not paths:
        raise click.ClickException("No feature files matched")

    adapter = PytestBddAdapter()
    parsed = [adapter.parse_feature_file(fp) for fp in sorted(paths)]

    if len(parsed) == 1:
        report = coverage_gate(parsed[0], ruleset_obj, ruleset_short_name=short_name)
        worst = report.gate_result.verdict
        if output_format.lower() == "json":
            body = render_coverage_json(report, ruleset_obj, feature_path=str(paths[0]))
        else:
            body = render_coverage_markdown(report, ruleset_obj, feature_path=str(paths[0]))
    else:
        report = coverage_gate_features(
            parsed, ruleset_obj, ruleset_short_name=short_name
        )
        worst = report.gate_result.verdict
        label = ", ".join(str(p) for p in sorted(paths))
        if output_format.lower() == "json":
            body = render_coverage_json(report, ruleset_obj, feature_path=label)
        else:
            body = render_coverage_markdown(report, ruleset_obj, feature_path=label)
        if not quiet:
            click.echo(
                f"Union coverage across {len(paths)} feature file(s).",
                err=True,
            )

    if quiet:
        label = "PASS" if worst == Verdict.PASS else "FAIL"
        click.echo(f"{label}: checked {len(paths)} feature(s)")
        if output is not None:
            output.write_text(body, encoding="utf-8")
    elif output is not None:
        output.write_text(body, encoding="utf-8")
        click.echo(f"Report written to {output}", err=True)
    else:
        click.echo(body)

    if worst != Verdict.PASS:
        sys.exit(1)
```

## Callee: pickled_rules.cli._resolve_ruleset_path (hop 1)

```python
def _resolve_ruleset_path(ruleset: str) -> Path:
    if ruleset in BUILTIN_RULESETS:
        return resolve_ruleset_name(ruleset)
    path = Path(ruleset)
    if not path.is_file():
        raise click.ClickException(f"Rule set file not found: {ruleset}")
    return path
```

## Unresolved callees

- `adapter.parse_feature_file` — variable 'adapter' reassigned; type not stable

## Notes

Collection stopped early because of --max-callees or --max-code-lines.
