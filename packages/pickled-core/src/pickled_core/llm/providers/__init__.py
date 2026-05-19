"""LLM provider adapters (optional SDK dependencies per provider)."""

from __future__ import annotations

__all__ = [
    "AnthropicClient",
    "GeminiClient",
    "OpenAIClient",
    "OpenAICompatClient",
]


def __getattr__(name: str) -> object:
    if name == "AnthropicClient":
        from pickled_core.llm.providers.anthropic import AnthropicClient

        return AnthropicClient
    if name == "OpenAIClient":
        from pickled_core.llm.providers.openai import OpenAIClient

        return OpenAIClient
    if name == "GeminiClient":
        from pickled_core.llm.providers.gemini import GeminiClient

        return GeminiClient
    if name == "OpenAICompatClient":
        from pickled_core.llm.providers.openai_compat import OpenAICompatClient

        return OpenAICompatClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
