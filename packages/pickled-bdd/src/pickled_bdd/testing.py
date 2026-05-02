"""Test doubles and hooks for `PICKLED_BDD_LLM_FACTORY` (tests, local experiments)."""

from __future__ import annotations

from pickled_core.llm.client import LLMClient


class CannedLLMClient:
    """Minimal LLMClient with fixed output for CLI integration tests."""

    def __init__(self, response: str) -> None:
        self._response = response

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
    ) -> str:
        _ = prompt, system
        return self._response


def build_fake_llm() -> LLMClient:
    """Import path for ``PICKLED_BDD_LLM_FACTORY`` in tests."""
    return CannedLLMClient(
        'Feature: CLI Smoke\n  Scenario: Example\n    Given the app is up\n',
    )
