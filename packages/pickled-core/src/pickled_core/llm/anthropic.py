"""Anthropic reference implementation of LLMClient.

This module imports `anthropic` lazily so that pickled-core does not pull
the SDK as a hard dependency. Construct `AnthropicClient` only when you
have installed the optional dependency:

    pip install pickled-core[anthropic]
"""

from __future__ import annotations

import os


class AnthropicClient:
    """Thin LLMClient wrapper around the official Anthropic SDK.

    Reads `ANTHROPIC_API_KEY` from the environment by default. Override
    via the `api_key` argument.
    """

    def __init__(
        self,
        *,
        model: str = "claude-opus-4-7",
        api_key: str | None = None,
        max_tokens: int = 4096,
    ) -> None:
        try:
            import anthropic  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError(
                "AnthropicClient requires the optional `anthropic` extra. "
                "Install it with: pip install pickled-core[anthropic]"
            ) from exc

        self._client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"),
        )
        self._model = model
        self._max_tokens = max_tokens

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
    ) -> str:
        """Send a single-turn message and return the text response."""
        kwargs: dict[str, object] = {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system is not None:
            kwargs["system"] = system

        response = self._client.messages.create(**kwargs)
        # The SDK returns a list of content blocks; we take the first text
        # block. If a future SDK version changes the shape, update here.
        for block in response.content:
            if getattr(block, "type", None) == "text":
                return str(block.text)
        return ""
