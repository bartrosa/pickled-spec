"""Tests for :class:`pickled_iac.advisor.IaCAdvisor`."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pickled_core.cost.models import TokenUsage
from pickled_core.llm.base import Completion, LLMClient, Message
from pickled_iac.advisor import IaCAdvisor


class _Canned(LLMClient):
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
        _ = messages, model, max_tokens, temperature, stop, extras
        return Completion(
            text=self._response,
            usage=TokenUsage(),
            model_id_resolved=model,
            raw_response=None,
        )

    def count_tokens(self, messages: list[Message], model: str) -> int:
        _ = messages, model
        return 1


def test_explain_returns_text_from_llm() -> None:
    llm = _Canned("Summary line\n\nRisk callouts\n\nFollow-ups")
    result = IaCAdvisor(llm).explain_plan_diff(plan_json='{"ok": true}')
    assert result.text == "Summary line\n\nRisk callouts\n\nFollow-ups"
    assert result.warnings == ()


def test_explain_warns_on_invalid_plan_json() -> None:
    llm = _Canned("still produced text")
    result = IaCAdvisor(llm).explain_plan_diff(plan_json="{not json")
    assert "not valid JSON" in result.warnings[0]
    assert result.text == "still produced text"


def test_remediate_warns_on_non_listdict_payload() -> None:
    llm = _Canned("remediation sections")
    result = IaCAdvisor(llm).suggest_security_remediation(
        trivy_findings_json='"a string"',
    )
    assert any("not list/dict" in w for w in result.warnings)
    assert result.text == "remediation sections"


def test_remediate_with_hcl_default_empty_string() -> None:
    llm = _Canned("ok")
    result = IaCAdvisor(llm).suggest_security_remediation(
        trivy_findings_json="[]",
        hcl_text="",
    )
    assert result.text == "ok"
    assert result.warnings == ()
