"""MCP tool registration for pickled-schema."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from fastmcp import FastMCP

from pickled_core import LLMClient

from pickled_schema.gates import SchemaCoverageFinding, SchemaCoverageGate
from pickled_schema.openapi.drafter import OpenAPIDrafter
from pickled_schema.openapi.parser import parse_openapi_text
from pickled_schema.openapi.validator import validate_openapi_dict
from pickled_schema.types import SchemaValidationError


def register_with_fastmcp(app: FastMCP, *, llm: LLMClient | None = None) -> None:
    """Register schema tools on a FastMCP application."""

    @app.tool(name="validate_openapi_spec")
    def validate_openapi_spec(*, spec_yaml: str) -> dict[str, Any]:
        """Validate an OpenAPI YAML document."""
        try:
            spec_dict, _ = parse_openapi_text(spec_yaml, suffix=".yaml")
            validate_openapi_dict(spec_dict)
        except SchemaValidationError as exc:
            return {"valid": False, "errors": exc.errors or [str(exc)]}
        except Exception as exc:  # noqa: BLE001 — surface parse errors to client
            return {"valid": False, "errors": [str(exc)]}
        return {"valid": True, "errors": []}

    @app.tool(name="check_schema_coverage")
    def check_schema_coverage(
        *,
        spec_yaml: str,
        feature_texts: list[str],
    ) -> dict[str, Any]:
        """Verify @schema:endpoint tags in features exist in the spec."""
        spec_dict, _ = parse_openapi_text(spec_yaml, suffix=".yaml")
        gate = SchemaCoverageGate()
        result = gate.run(
            spec_dict,
            context={"feature_texts": feature_texts},
        )
        findings = [
            {"tag": f.tag, "source": f.source}
            for f in result.findings
            if isinstance(f, SchemaCoverageFinding)
        ]
        return {
            "verdict": result.verdict.value,
            "notes": result.notes,
            "findings": findings,
        }

    @app.tool(name="draft_openapi_endpoint")
    def draft_openapi_endpoint(
        *,
        method: str,
        path: str,
        gherkin_text: str,
    ) -> dict[str, Any]:
        """Draft an OpenAPI 3.1 path item from Gherkin text."""
        if llm is None:
            msg = "LLM client not configured"
            raise RuntimeError(msg)
        try:
            artifact = OpenAPIDrafter(llm).draft_endpoint(
                method,
                path,
                gherkin_text,
            )
            validation_passed = True
            schema_yaml = artifact.content
        except SchemaValidationError as exc:
            validation_passed = False
            schema_yaml = yaml.safe_dump(
                {"error": str(exc), "details": exc.errors},
                default_flow_style=False,
            )
        return {
            "schema_yaml": schema_yaml,
            "validation_passed": validation_passed,
        }


__all__ = ["register_with_fastmcp"]
