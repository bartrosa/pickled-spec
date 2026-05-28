# Code context: draft

- **Surface id:** pickled_schema_draft
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 5 | **Total lines:** 128 | **Truncated:** False

## Root: pickled_schema.cli.draft

```python
def draft(
    method: str,
    endpoint_path: str,
    gherkin_file: Path,
    output: Path | None,
) -> None:
    """Draft an OpenAPI 3.1 path item from a Gherkin scenario."""
    gherkin = gherkin_file.read_text(encoding="utf-8")
    llm = _build_llm_client()
    artifact = OpenAPIDrafter(llm).draft_endpoint(
        method,
        endpoint_path,
        gherkin,
    )
    if output:
        output.write_text(artifact.content, encoding="utf-8")
        click.echo(f"Wrote {output}", err=True)
    else:
        click.echo(artifact.content)
```

## Callee: pickled_schema.cli._build_llm_client (hop 1)

```python
def _build_llm_client() -> LLMClient:
    factory = os.environ.get("PICKLED_SCHEMA_LLM_FACTORY")
    if factory:
        module_name, sep, attr = factory.partition(":")
        if not sep:
            raise click.ClickException(
                "PICKLED_SCHEMA_LLM_FACTORY must be 'module:callable'"
            )
        module = importlib.import_module(module_name)
        return cast(LLMClient, getattr(module, attr)())

    from pickled_core.llm.config import load_config
    from pickled_core.llm.factory import build_client

    provider = os.environ.get("PICKLED_LLM_PROVIDER", "anthropic")
    try:
        return build_client(provider, config=load_config())
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc
```

## Callee: pickled_schema.openapi.OpenAPIDrafter.draft_endpoint (hop 1)

```python
def draft_endpoint(
        self,
        method: str,
        path: str,
        gherkin_context: str,
        existing_component_names: list[str] | None = None,
    ) -> SchemaArtifact:
        """Draft, validate, and return a path-item ``SchemaArtifact``."""
        method_upper = method.upper()
        components = existing_component_names or []
        last_error = ""
        path_item: dict[str, Any] | None = None

        for _attempt in range(3):
            extra = f"\n\nPrevious validation errors:\n{last_error}" if last_error else ""
            prompt = self._template.render(
                method=method_upper,
                path=path,
                gherkin_context=gherkin_context + extra,
                existing_component_names=", ".join(components) or "(none)",
            )
            from pickled_core.llm.turns import complete_prompt

            raw = complete_prompt(
                self._llm,
                prompt,
                system="Output only YAML for the path item. No fences, no prose.",
            )
            loaded = yaml.safe_load(raw.strip())
            if not isinstance(loaded, dict):
                last_error = "LLM output is not a YAML mapping"
                continue
            path_item = _unwrap_path_item(loaded, method.lower())
            envelope = {
                "openapi": "3.1.0",
                "info": {"title": "draft", "version": "0.0.0"},
                "paths": {path: {method.lower(): path_item}},
                "components": {"schemas": {}},
            }
            try:
                validate_openapi_dict(envelope)
            except SchemaValidationError as exc:
                last_error = "; ".join(exc.errors) or str(exc)
                continue
            yaml_out = yaml.safe_dump(
                path_item,
                sort_keys=False,
                default_flow_style=False,
            )
            return SchemaArtifact(
                format=SchemaFormat.openapi_3_1,
                content=yaml_out,
                endpoint_id=f"{method_upper}-{path}",
                source="draft",
            )

        msg = f"failed to draft valid OpenAPI after 3 attempts: {last_error}"
        raise SchemaValidationError(msg, errors=[last_error] if last_error else [])
```

## Callee: pickled_schema.openapi._unwrap_path_item (hop 2)

```python
def _unwrap_path_item(loaded: dict[str, Any], method: str) -> dict[str, Any]:
    """Accept a bare operation object or a one-key path-item wrapper."""
    if method in loaded and all(k in _HTTP_METHODS for k in loaded):
        op = loaded[method]
        return op if isinstance(op, dict) else loaded
    if len(loaded) == 1:
        only_key = next(iter(loaded))
        if only_key in _HTTP_METHODS:
            inner = loaded[only_key]
            if isinstance(inner, dict):
                return inner
    return loaded
```

## Callee: pickled_schema.openapi.validator.validate_openapi_dict (hop 2)

```python
def validate_openapi_dict(spec_dict: dict[str, Any]) -> None:
    """Validate *spec_dict* with openapi-spec-validator."""
    try:
        from openapi_spec_validator import validate
        from openapi_spec_validator.exceptions import OpenAPIError
        from openapi_spec_validator.validation.exceptions import (
            OpenAPIValidationError,
        )
    except ImportError as exc:
        msg = "install pickled-schema[openapi] for OpenAPI validation"
        raise SchemaValidationError(msg) from exc

    try:
        validate(spec_dict)
    except (OpenAPIError, OpenAPIValidationError) as exc:
        errors = [str(exc)]
        nested = getattr(exc, "schema_errors", None)
        if nested:
            errors.extend(str(e) for e in nested)
        raise SchemaValidationError("OpenAPI validation failed", errors=errors) from exc
```

## Unresolved callees

- `factory.partition` — variable 'factory' reassigned; type not stable
- `getattr(module, attr)()` — dynamic attribute access
- `getattr(module, attr)` — dynamic attribute access
- `self._template.render` — protocol or unknown attribute type
