"""Single-turn helpers for gates and drafters."""

from __future__ import annotations

from pickled_core.llm.base import LLMClient, Message

DEFAULT_MODEL = "claude-3-5-sonnet-20241022"


def complete_prompt(
    client: LLMClient,
    prompt: str,
    *,
    system: str | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4096,
) -> str:
    """Run one user turn and return the assistant text."""
    messages: list[Message] = []
    if system:
        messages.append(Message(role="system", content=system))
    messages.append(Message(role="user", content=prompt))
    result = client.complete(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        temperature=None,
        stop=None,
        extras=None,
    )
    return result.text


__all__ = ["DEFAULT_MODEL", "complete_prompt"]
