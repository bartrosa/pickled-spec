"""LLMClient protocol — vendor-neutral text-completion interface."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """A minimal text-in / text-out interface.

    Implementations may be cloud-backed (Anthropic, OpenAI, ...) or local
    (Ollama, llama.cpp, ...). Gates and drafters depend only on this
    protocol — never on a concrete vendor SDK.
    """

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
    ) -> str:
        """Return the model's completion for `prompt`.

        `system` is an optional system message. Implementations that do
        not have a separate system slot should prepend it to `prompt`.
        """
        ...
