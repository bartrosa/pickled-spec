# Code context: draft

- **Surface id:** pickled_bdd_draft
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 3 | **Total lines:** 40 | **Truncated:** False

## Root: pickled_bdd.cli.draft

```python
def draft(story_file: str, output: str | None) -> None:
    """Draft a .feature file from a user story (Markdown)."""
    story = Path(story_file).read_text(encoding="utf-8")
    llm = _build_llm_client()
    result = FeatureDrafter(llm).draft_from_story(story)

    if output:
        Path(output).write_text(result.text, encoding="utf-8")
        click.echo(f"Wrote {output}", err=True)
    else:
        click.echo(result.text)
```

## Callee: pickled_bdd.cli._build_llm_client (hop 1)

```python
def _build_llm_client() -> LLMClient:
    """Build an LLM client. Override via PICKLED_BDD_LLM_FACTORY for tests."""
    from pickled_core.llm.bootstrap import build_default_client
    from pickled_core.llm.config import ConfigError

    try:
        return build_default_client(factory_env="PICKLED_BDD_LLM_FACTORY")
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc
```

## Callee: pickled_bdd.FeatureDrafter.draft_from_story (hop 1)

```python
def draft_from_story(self, story: str) -> DraftResult:
        """Send the story to the LLM and return a DraftResult.

        The drafter does not validate the returned Gherkin; that is the
        Ambiguity gate's job (PR-08). v0.1 returns the raw text and
        leaves a generic rationale string.
        """
        prompt = self._template.render(story=story)
        from pickled_core.llm.turns import complete_prompt

        feature_text = complete_prompt(
            self._llm,
            prompt,
            system="You output only Gherkin. No prose, no fences.",
        )
        return DraftResult(
            text=feature_text.strip(),
            rationale="LLM-drafted from user story; no post-processing applied.",
            warnings=(),
        )
```

## Unresolved callees

- `self._template.render` — protocol or unknown attribute type
