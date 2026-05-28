"""Tests for :func:`pickled_core.llm.sanitize.strip_markdown_fence`."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any
from unittest.mock import patch

import pytest
from pickled_core.llm.sanitize import strip_markdown_fence

_GHERKIN_BODY = "Feature: Auth\n  Scenario: Login\n    Given a user\n"
_VALID_RULESET = """metadata:
  source_id: test-src
  source_title: Test Rules
  applies_to: internal-api
  maintainer: tests
  source_version: '1.0'
  active_from: '2026-05-25'
rules:
  - id: api-naming
    title: Use consistent paths
    description: REST paths use kebab-case resource names.
    enforcement: strict
"""
_VALID_SQL = """-- intent: add column
CREATE TABLE users (id INTEGER PRIMARY KEY);
"""
_VALID_CORPUS = json.dumps([{"name": "a", "payload": "1"}])
_VALID_HCL = 'resource "aws_s3_bucket" "x" {\n  bucket = "example"\n}\n'
_VALID_OPENAPI = """get:
  summary: List users
  operationId: listUsers
  responses:
    '200':
      description: OK
"""


def test_strips_gherkin_fence() -> None:
    fenced = f"```gherkin\n{_GHERKIN_BODY}\n```"
    assert strip_markdown_fence(fenced) == _GHERKIN_BODY.strip()


def test_strips_fence_no_language() -> None:
    body = "line one\nline two"
    fenced = f"```\n{body}\n```"
    assert strip_markdown_fence(fenced) == body


def test_strips_yaml_json_hcl_fences() -> None:
    yaml_body = "key: value\n"
    json_body = '{"a": 1}'
    hcl_body = 'resource "x" "y" {}'
    assert strip_markdown_fence(f"```yaml\n{yaml_body}\n```") == yaml_body.strip()
    assert strip_markdown_fence(f"```json\n{json_body}\n```") == json_body
    assert strip_markdown_fence(f"```hcl\n{hcl_body}\n```") == hcl_body


def test_unfenced_text_unchanged() -> None:
    assert strip_markdown_fence(_GHERKIN_BODY) == _GHERKIN_BODY.strip()


def test_inner_fence_preserved() -> None:
    text = (
        "Feature: Docs\n"
        "  Scenario: Example\n"
        "    Given a snippet:\n"
        "      ```python\n"
        "      print(1)\n"
        "      ```\n"
    )
    assert strip_markdown_fence(text) == text.strip()


def test_idempotent() -> None:
    fenced = f"```gherkin\n{_GHERKIN_BODY}\n```"
    once = strip_markdown_fence(fenced)
    assert strip_markdown_fence(once) == once


def test_whitespace_around_fence_handled() -> None:
    fenced = f"  \n```gherkin\n{_GHERKIN_BODY}\n```  \n"
    assert strip_markdown_fence(fenced) == _GHERKIN_BODY.strip()


def test_empty_string() -> None:
    assert strip_markdown_fence("") == ""
    assert strip_markdown_fence("   \n  ") == ""


def test_fence_with_trailing_prose_not_stripped() -> None:
    fenced = "```\nbody\n```\nextra line"
    assert strip_markdown_fence(fenced) == fenced.strip()


def test_feature_drafter_strips_fence() -> None:
    from pickled_bdd.drafter import FeatureDrafter
    from pickled_core.cost.models import TokenUsage
    from pickled_core.llm.base import Completion, LLMClient, Message

    class FakeLLM(LLMClient):
        provider_key = "fake"

        def complete(
            self,
            *,
            messages: list[Message],
            model: str,
            max_tokens: int,
            temperature: float | None,
            stop: list[str] | None,
            extras: Mapping[str, Any] | None,
        ) -> Completion:
            _ = messages, model, max_tokens, temperature, stop, extras
            return Completion(
                text=f"```gherkin\n{_GHERKIN_BODY}\n```",
                usage=TokenUsage(),
                model_id_resolved=model,
                raw_response=None,
            )

        def count_tokens(self, messages: list[Message], model: str) -> int:
            _ = messages, model
            return 1

    result = FeatureDrafter(FakeLLM()).draft_from_story("story")
    assert result.text == _GHERKIN_BODY.strip()
    assert "```" not in result.text


def test_rules_drafter_strips_fence() -> None:
    from pickled_bdd.testing import CannedLLMClient
    from pickled_rules.drafter import RuleSetDrafter

    fenced = f"```yaml\n{_VALID_RULESET}\n```"
    result = RuleSetDrafter(CannedLLMClient(fenced)).draft_from_brief(
        brief_text="API naming",
        ruleset_short_name="api",
        source_id="test-src",
        applies_to="internal-api",
        active_from="2026-05-25",
    )
    assert result.text.startswith("metadata:")
    assert "```" not in result.text


def test_migration_drafter_strips_fence() -> None:
    from pickled_bdd.testing import CannedLLMClient
    from pickled_data.drafter import MigrationDrafter

    fenced = f"```sql\n{_VALID_SQL}\n```"
    result = MigrationDrafter(CannedLLMClient(fenced)).draft_from_intent(
        intent_text="add table",
        dialect="sqlite",
    )
    assert result.text.startswith("-- intent:")
    assert "```" not in result.text


def test_corpus_drafter_strips_fence() -> None:
    from pickled_bdd.testing import CannedLLMClient
    from pickled_diff.drafter import CorpusDrafter

    fenced = f"```json\n{_VALID_CORPUS}\n```"
    result = CorpusDrafter(CannedLLMClient(fenced)).draft_from_examples(
        seed_examples=[{"name": "a", "payload": "1"}],
        target_size=1,
    )
    assert len(result.items) == 1
    assert result.items[0]["name"] == "a"


def test_openapi_drafter_strips_fence() -> None:
    pytest.importorskip("openapi_spec_validator")

    from pickled_core.cost.models import TokenUsage
    from pickled_core.llm.base import Completion, LLMClient, Message
    from pickled_schema.openapi.drafter import OpenAPIDrafter

    class FakeLLM(LLMClient):
        provider_key = "fake"

        def complete(
            self,
            *,
            messages: list[Message],
            model: str,
            max_tokens: int,
            temperature: float | None,
            stop: list[str] | None,
            extras: Mapping[str, Any] | None,
        ) -> Completion:
            _ = messages, model, max_tokens, temperature, stop, extras
            return Completion(
                text=f"```yaml\n{_VALID_OPENAPI}\n```",
                usage=TokenUsage(),
                model_id_resolved=model,
                raw_response=None,
            )

        def count_tokens(self, messages: list[Message], model: str) -> int:
            _ = messages, model
            return 1

    artifact = OpenAPIDrafter(FakeLLM()).draft_endpoint(
        "GET",
        "/users",
        "Scenario: List users",
    )
    assert "summary: List users" in artifact.content
    assert "```" not in artifact.content


def test_iac_drafter_strips_fence() -> None:
    from pickled_core.cost.models import TokenUsage
    from pickled_core.llm.base import Completion, LLMClient, Message
    from pickled_iac.drafter import IaCDrafter
    from pickled_iac.types import ValidateResult

    class FakeLLM(LLMClient):
        provider_key = "fake"

        def complete(
            self,
            *,
            messages: list[Message],
            model: str,
            max_tokens: int,
            temperature: float | None,
            stop: list[str] | None,
            extras: Mapping[str, Any] | None,
        ) -> Completion:
            _ = messages, model, max_tokens, temperature, stop, extras
            return Completion(
                text=f"```hcl\n{_VALID_HCL}\n```",
                usage=TokenUsage(),
                model_id_resolved=model,
                raw_response=None,
            )

        def count_tokens(self, messages: list[Message], model: str) -> int:
            _ = messages, model
            return 1

    with (
        patch("pickled_iac.drafter.iac_binary", return_value="terraform"),
        patch(
            "pickled_iac.drafter.validate",
            return_value=ValidateResult(valid=True, diagnostics=()),
        ),
    ):
        artifact = IaCDrafter(FakeLLM()).draft_module("provision bucket")
    assert artifact.content.strip() == _VALID_HCL.strip()
    assert "```" not in artifact.content
