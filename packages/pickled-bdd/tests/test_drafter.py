from __future__ import annotations

from pickled_bdd.drafter import FeatureDrafter
from pickled_core import DraftResult


class FakeLLMClient:
    """Captures prompts for assertions."""

    def __init__(self, response: str = "Feature: X\n  Scenario: Y\n    Given z\n") -> None:
        self.response = response
        self.last_prompt = ""
        self.last_system: str | None = None

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
    ) -> str:
        self.last_prompt = prompt
        self.last_system = system
        return self.response


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
    assert story in fake.last_prompt
    assert "User story:" in fake.last_prompt


def test_system_message_is_gherkin_only() -> None:
    fake = FakeLLMClient()
    FeatureDrafter(fake).draft_from_story("Story body")
    assert fake.last_system == "You output only Gherkin. No prose, no fences."
