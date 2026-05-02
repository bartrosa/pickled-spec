from __future__ import annotations

import builtins
from typing import Any

import pytest
from pickled_core.llm import LLMClient
from pickled_core.llm.anthropic import AnthropicClient


class FakeLLMClient:
    def __init__(self, reply: str = "ok") -> None:
        self._reply = reply

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
    ) -> str:
        _ = prompt, system
        return self._reply


def test_fake_llm_satisfies_protocol() -> None:
    fake = FakeLLMClient("configured-reply")
    assert isinstance(fake, LLMClient)
    assert fake.complete("hello") == "configured-reply"


def test_anthropic_client_raises_helpful_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def import_without_anthropic(
        name: str,
        globals: dict[str, Any] | None = None,
        locals: dict[str, Any] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> Any:
        if name == "anthropic":
            raise ImportError("No module named 'anthropic'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_anthropic)

    with pytest.raises(ImportError, match=r"pickled-core\[anthropic\]"):
        AnthropicClient()
