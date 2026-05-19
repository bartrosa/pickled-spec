from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pickled_bdd.drafter import FeatureDrafter
from pickled_core import DraftResult
from pickled_core.cost.models import TokenUsage
from pickled_core.llm.base import Completion, LLMClient, Message


class FakeLLMClient(LLMClient):
    """Captures prompts for assertions."""

    provider_key = "fake"

    def __init__(self, response: str = "Feature: X\n  Scenario: Y\n    Given z\n") -> None:
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


def test_drafter_returns_draft_result_with_fake_response() -> None:
    fake = FakeLLMClient(
        response="Feature: Auth\n  Scenario: Login\n    Given a user\n",
    )
    drafter = FeatureDrafter(fake)
    result = drafter.draft_from_story("As a user I want login")

    assert isinstance(result, DraftResult)
    assert result.text == fake.response.strip()
    assert "LLM-drafted" in result.rationale
    assert result.warnings == ()


def test_story_text_embedded_in_rendered_prompt() -> None:
    story = "As a customer I want checkout"
    fake = FakeLLMClient()
    FeatureDrafter(fake).draft_from_story(story)
    user_content = next(m.content for m in fake.last_messages if m.role == "user")
    assert story in user_content
    assert "User story:" in user_content


def test_system_message_is_gherkin_only() -> None:
    fake = FakeLLMClient()
    FeatureDrafter(fake).draft_from_story("Story body")
    system = next((m.content for m in fake.last_messages if m.role == "system"), None)
    assert system == "You output only Gherkin. No prose, no fences."
