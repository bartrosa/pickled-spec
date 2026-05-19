"""Test doubles and hooks for `PICKLED_BDD_LLM_FACTORY` (tests, local experiments)."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

from pickled_core.cost.models import TokenUsage
from pickled_core.llm.base import Completion, LLMClient, Message


class CannedLLMClient(LLMClient):
    """Minimal LLMClient with fixed output for CLI integration tests."""

    provider_key = "canned"

    def __init__(self, response: str) -> None:
        self._response = response

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
            text=self._response,
            usage=TokenUsage(),
            model_id_resolved=model,
            raw_response=None,
        )

    def count_tokens(self, messages: list[Message], model: str) -> int:
        _ = model
        return sum(len(m.content) for m in messages) // 4 or 1


def build_fake_llm() -> LLMClient:
    """Import path for ``PICKLED_BDD_LLM_FACTORY`` in tests."""
    return CannedLLMClient(
        'Feature: CLI Smoke\n  Scenario: Example\n    Given the app is up\n',
    )


_OK_JSON = '{"is_ambiguous": false, "alternatives": [], "suggested_fix": ""}'


def build_check_pass_llm() -> LLMClient:
    """Ambiguity gate: every scenario is judged unambiguous."""
    return CannedLLMClient(_OK_JSON)


def build_check_warn_llm() -> LLMClient:
    """First scenario ambiguous, remaining scenarios unambiguous (for 4-scenario feature)."""
    ambiguous = (
        '{"is_ambiguous": true, "alternatives": ["A path", "B path"], '
        '"suggested_fix": "Clarify acceptance"}'
    )
    replies: Iterator[str] = iter([ambiguous, _OK_JSON, _OK_JSON, _OK_JSON])

    class _FirstAmbiguous(CannedLLMClient):
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
            try:
                text = next(replies)
            except StopIteration:
                text = _OK_JSON
            return Completion(
                text=text,
                usage=TokenUsage(),
                model_id_resolved=model,
                raw_response=None,
            )

    return _FirstAmbiguous(_OK_JSON)
