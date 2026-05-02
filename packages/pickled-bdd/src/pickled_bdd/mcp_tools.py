"""MCP tool registration for pickled-bdd.

After `register(server)` is called, the server's registry contains:

- `draft_feature_from_story` — wraps FeatureDrafter.
- `validate_feature_ambiguity` — wraps AmbiguityGate.

Transport is deferred to v0.1.1; this module is invoked today by the
CLI's `serve` command and by the test suite.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from pickled_core import AmbiguityFinding, LLMClient, PickledMCPServer

from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
from pickled_bdd.drafter import FeatureDrafter
from pickled_bdd.gates.ambiguity import AmbiguityGate


def register(server: PickledMCPServer, *, llm: LLMClient) -> None:
    """Register pickled-bdd's tools with the server.

    Caller provides the LLM client; the same client is shared by both
    tool handlers. Test code passes a fake; CLI passes AnthropicClient.
    """
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

    def validate_feature_ambiguity(
        *,
        feature_text: str,
    ) -> dict[str, Any]:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".feature",
            delete=False,
            encoding="utf-8",
        ) as fp:
            fp.write(feature_text)
            tmp_path = Path(fp.name)
        try:
            feature = adapter.parse_feature_file(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

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
