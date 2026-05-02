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

    class _FirstAmbiguous:
        def __init__(self) -> None:
            self._first = True

        def complete(
            self,
            prompt: str,
            *,
            system: str | None = None,
        ) -> str:
            _ = prompt, system
            if self._first:
                self._first = False
                return ambiguous
            return _OK_JSON

    return _FirstAmbiguous()
