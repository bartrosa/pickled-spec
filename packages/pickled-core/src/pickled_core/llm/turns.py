"""Single-turn helpers for gates and drafters."""

from __future__ import annotations

from pickled_core.llm.base import LLMClient, Message

DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


def complete_prompt(
    client: LLMClient,
    prompt: str,
    *,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int = 4096,
) -> str:
    """Run one user turn and return the assistant text.

    Model resolution order:
    1. explicit ``model=`` argument
    2. ``client.default_model`` if set
    3. module-level ``DEFAULT_MODEL`` (last resort)
    """
    resolved_model = model or getattr(client, "default_model", None) or DEFAULT_MODEL
    messages: list[Message] = []
    if system:
        messages.append(Message(role="system", content=system))
    messages.append(Message(role="user", content=prompt))
    result = client.complete(
        messages=messages,
        model=resolved_model,
        max_tokens=max_tokens,
        temperature=None,
        stop=None,
        extras=None,
    )
    return result.text


__all__ = ["DEFAULT_MODEL", "complete_prompt"]
