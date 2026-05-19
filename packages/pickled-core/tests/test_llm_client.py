from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

pytest.importorskip("anthropic")
from pickled_core.cost.models import TokenUsage
from pickled_core.llm import LLMClient
from pickled_core.llm.base import Completion, Message
from pickled_core.llm.providers.anthropic import AnthropicClient


class FakeLLMClient(LLMClient):
    provider_key = "fake"

    def __init__(self, reply: str = "ok") -> None:
        self._reply = reply

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
        _ = messages, max_tokens, temperature, stop, extras
        return Completion(
            text=self._reply,
            usage=TokenUsage(),
            model_id_resolved=model,
            raw_response=None,
        )

    def count_tokens(self, messages: list[Message], model: str) -> int:
        _ = model
        return 1


def test_fake_is_llm_client() -> None:
    fake = FakeLLMClient("configured-reply")
    assert isinstance(fake, LLMClient)
    out = fake.complete(
        messages=[Message(role="user", content="hello")],
        model="m",
        max_tokens=10,
        temperature=None,
        stop=None,
        extras=None,
    )
    assert out.text == "configured-reply"


def test_anthropic_module_importable() -> None:
    pytest.importorskip("anthropic")
    from pickled_core.cost import load_default_catalogue

    client = AnthropicClient(api_key="k", catalogue=load_default_catalogue())
    assert client.provider_key == "anthropic"
