"""LLM-driven OpenAPI path-item drafter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pickled_core import LLMClient, PromptTemplate
from pickled_core.llm.sanitize import strip_markdown_fence
from pickled_core.llm.turns import complete_prompt

from pickled_schema.openapi.validator import validate_openapi_dict
from pickled_schema.types import SchemaArtifact, SchemaFormat, SchemaValidationError


def _prompt_path(name: str) -> Path:
    return Path(__file__).resolve().parent / "prompts" / name


_HTTP_METHODS = frozenset({"get", "post", "put", "patch", "delete", "head", "options", "trace"})


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


class OpenAPIDrafter:
    """Draft a single OpenAPI 3.1 path item from Gherkin context."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm
        self._template = PromptTemplate.from_file(_prompt_path("draft.md"))

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
            raw = complete_prompt(
                self._llm,
                prompt,
                system="Output only YAML for the path item. No fences, no prose.",
            )
            loaded = yaml.safe_load(strip_markdown_fence(raw))
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


__all__ = ["OpenAPIDrafter"]
