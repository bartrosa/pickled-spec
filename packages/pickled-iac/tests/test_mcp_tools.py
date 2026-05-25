"""MCP tool surface tests for pickled-iac."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pickled_core.cost.models import TokenUsage
from pickled_core.llm.base import Completion, LLMClient, Message
from pickled_iac.mcp_tools import register_with_fastmcp


class _FakeApp:
    def __init__(self) -> None:
        self.tools: dict[str, object] = {}

    def tool(self, *, name: str | None = None):  # type: ignore[no-untyped-def]
        def deco(fn):  # type: ignore[no-untyped-def]
            assert name is not None
            self.tools[name] = fn
            return fn

        return deco


class _Canned(LLMClient):
    provider_key = "canned"

    def __init__(self, response: str = "advisor text") -> None:
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


def test_register_adds_explain_plan_diff_and_suggest_security_remediation() -> None:
    app = _FakeApp()
    register_with_fastmcp(app, llm=_Canned())  # type: ignore[arg-type]
    names = set(app.tools.keys())
    assert "explain_plan_diff" in names
    assert "suggest_security_remediation" in names
    assert "draft_terraform_module" in names


def test_explain_plan_diff_raises_when_no_llm() -> None:
    app = _FakeApp()
    register_with_fastmcp(app, llm=None)  # type: ignore[arg-type]
    handler = app.tools["explain_plan_diff"]
    try:
        handler(plan_json="{}")  # type: ignore[operator]
    except RuntimeError as exc:
        assert "PICKLED_IAC_LLM_FACTORY" in str(exc)
    else:
        raise AssertionError("expected RuntimeError when llm is None")
