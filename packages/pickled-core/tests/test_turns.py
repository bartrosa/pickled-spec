"""Tests for :func:`pickled_core.llm.turns.complete_prompt` model resolution."""

from __future__ import annotations

from typing import Any

from pickled_core.cost.models import TokenUsage
from pickled_core.llm.base import Completion, LLMClient, Message
from pickled_core.llm.turns import DEFAULT_MODEL, complete_prompt


class _CaptureClient(LLMClient):
    provider_key = "capture"

    def __init__(self, *, default_model: str | None = None) -> None:
        self.captured_model: str | None = None
        if default_model is not None:
            self.default_model = default_model

    def complete(
        self,
        *,
        messages: list[Message],
        model: str,
        max_tokens: int,
        temperature: float | None,
        stop: list[str] | None,
        extras: dict[str, Any] | None,
    ) -> Completion:
        _ = messages, max_tokens, temperature, stop, extras
        self.captured_model = model
        return Completion(
            text="ok",
            usage=TokenUsage(input=1, output=1),
            model_id_resolved=model,
            raw_response={},
        )

    def count_tokens(self, messages: list[Message], model: str) -> int:
        _ = messages, model
        return 1


def test_explicit_model_wins() -> None:
    client = _CaptureClient()
    complete_prompt(
        client,
        "hi",
        model="claude-haiku-4-5-20251001",
    )
    assert client.captured_model == "claude-haiku-4-5-20251001"


def test_client_default_model_used_when_not_overridden() -> None:
    client = _CaptureClient(default_model="claude-sonnet-4-5-20250929")
    complete_prompt(client, "hi")
    assert client.captured_model == "claude-sonnet-4-5-20250929"


def test_module_default_model_is_last_resort() -> None:
    client = _CaptureClient()
    complete_prompt(client, "hi")
    assert client.captured_model == DEFAULT_MODEL


def test_default_model_constant_is_current() -> None:
    assert DEFAULT_MODEL == "claude-sonnet-4-5-20250929"
