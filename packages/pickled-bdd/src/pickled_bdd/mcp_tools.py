"""MCP tool registration for pickled-bdd.

After ``register`` or ``register_with_fastmcp`` is called:

- ``draft_feature_from_story`` — wraps FeatureDrafter.
- ``validate_feature_ambiguity`` — wraps AmbiguityGate.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pickled_core import AmbiguityFinding, LLMClient, PickledMCPServer

if TYPE_CHECKING:
    from fastmcp import FastMCP

from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
from pickled_bdd.drafter import FeatureDrafter
from pickled_bdd.gates.ambiguity import AmbiguityGate


def _build_handlers(
    llm: LLMClient,
) -> tuple[
    Any,
    Any,
]:
    drafter = FeatureDrafter(llm)
    gate = AmbiguityGate(llm)
    adapter = PytestBddAdapter()

    def draft_feature_from_story(*, story_text: str) -> dict[str, Any]:
        result = drafter.draft_from_story(story_text)
        return {
            "feature_text": result.text,
            "rationale": result.rationale,
            "warnings": list(result.warnings),
        }

    def validate_feature_ambiguity(*, feature_text: str) -> dict[str, Any]:
        feature = adapter.parse_feature_text(feature_text)
        result = gate.run(feature)
        return {
            "verdict": result.verdict.value,
            "notes": result.notes,
            "findings": [
                {
                    "scenario": f.target_name,
                    "alternatives": list(f.alternatives),
                    "suggested_fix": f.suggested_fix,
                }
                for f in result.findings
                if isinstance(f, AmbiguityFinding)
            ],
        }

    return draft_feature_from_story, validate_feature_ambiguity


def register_with_fastmcp(app: FastMCP, *, llm: LLMClient | None = None) -> None:
    """Register tools directly on a FastMCP application."""
    if llm is not None:
        draft_feature_from_story, validate_feature_ambiguity = _build_handlers(llm)
    else:

        def draft_feature_from_story(*, story_text: str) -> dict[str, Any]:
            _ = story_text
            msg = "LLM client not configured (set pickled.config.yaml or PICKLED_BDD_LLM_FACTORY)"
            raise RuntimeError(msg)

        def validate_feature_ambiguity(*, feature_text: str) -> dict[str, Any]:
            _ = feature_text
            msg = "LLM client not configured (set pickled.config.yaml or PICKLED_BDD_LLM_FACTORY)"
            raise RuntimeError(msg)

    @app.tool(name="draft_feature_from_story")
    def _draft(*, story_text: str) -> dict[str, Any]:
        """Draft a Gherkin .feature file from a natural-language user story."""
        out: dict[str, Any] = draft_feature_from_story(story_text=story_text)
        return out

    @app.tool(name="validate_feature_ambiguity")
    def _validate(*, feature_text: str) -> dict[str, Any]:
        """Run the ambiguity gate against a Gherkin .feature file."""
        out: dict[str, Any] = validate_feature_ambiguity(feature_text=feature_text)
        return out


def register(server: PickledMCPServer, *, llm: LLMClient) -> None:
    """Register pickled-bdd's tools with a :class:`PickledMCPServer`."""
    draft_feature_from_story, validate_feature_ambiguity = _build_handlers(llm)

    server.register_tool(
        "draft_feature_from_story",
        draft_feature_from_story,
        description=(
            "Draft a Gherkin .feature file from a natural-language user "
            "story. Returns the feature text plus a short rationale and "
            "any warnings."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "story_text": {
                    "type": "string",
                    "description": "User story in Markdown or plain text.",
                },
            },
            "required": ["story_text"],
        },
    )

    server.register_tool(
        "validate_feature_ambiguity",
        validate_feature_ambiguity,
        description=(
            "Run the ambiguity gate against a Gherkin .feature file. "
            "Returns verdict (pass/warn/fail), notes, and per-scenario "
            "findings with suggested fixes."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "feature_text": {
                    "type": "string",
                    "description": "Full Gherkin feature text.",
                },
            },
            "required": ["feature_text"],
        },
    )


__all__ = ["register", "register_with_fastmcp"]
