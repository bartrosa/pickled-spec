from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

openapi_spec_validator = pytest.importorskip("openapi_spec_validator")

from pickled_core.cost.models import TokenUsage  # noqa: E402
from pickled_core.llm.base import Completion, LLMClient, Message  # noqa: E402
from pickled_schema.openapi.drafter import OpenAPIDrafter  # noqa: E402
from pickled_schema.types import SchemaFormat  # noqa: E402

_VALID_PATH_ITEM = """
get:
  summary: List users
  operationId: listUsers
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            type: array
            items:
              type: object
              properties:
                id:
                  type: string
"""


class FakeLLMClient(LLMClient):
    provider_key = "fake"

    def __init__(self, response: str) -> None:
        self.response = response
        self.last_messages: list[Message] = []

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
        _ = model, max_tokens, temperature, stop, extras
        self.last_messages = list(messages)
        return Completion(
            text=self.response,
            usage=TokenUsage(),
            model_id_resolved=model,
            raw_response=None,
        )

    def count_tokens(self, messages: list[Message], model: str) -> int:
        _ = messages, model
        return 1


def test_drafter_returns_validated_artifact() -> None:
    fake = FakeLLMClient(_VALID_PATH_ITEM)
    artifact = OpenAPIDrafter(fake).draft_endpoint(
        "GET",
        "/users",
        "Scenario: List users\n  When I request the user list\n  Then I see users",
    )
    assert artifact.format is SchemaFormat.openapi_3_1
    assert artifact.endpoint_id == "GET-/users"
    assert artifact.source == "draft"
    assert "summary: List users" in artifact.content


def test_gherkin_in_prompt() -> None:
    gherkin = "Scenario: Create\n  When I POST a user"
    fake = FakeLLMClient(_VALID_PATH_ITEM)
    OpenAPIDrafter(fake).draft_endpoint("POST", "/users", gherkin)
    user_msg = next(m.content for m in fake.last_messages if m.role == "user")
    assert gherkin in user_msg
