"""MCP tool surface tests for pickled-data."""

from __future__ import annotations

from pickled_bdd.testing import CannedLLMClient
from pickled_data.mcp_tools import register_with_fastmcp


class _FakeApp:
    def __init__(self) -> None:
        self.tools: dict[str, object] = {}

    def tool(self, *, name: str | None = None):  # type: ignore[no-untyped-def]
        def deco(fn):  # type: ignore[no-untyped-def]
            assert name is not None
            self.tools[name] = fn
            return fn

        return deco


_VALID_SQL = """-- intent: add column
ALTER TABLE users ADD COLUMN deleted_at TEXT;
---RATIONALE---
ok
"""


def _build_tools(*, llm: object | None = None) -> dict[str, object]:
    app = _FakeApp()
    register_with_fastmcp(app, llm=llm)  # type: ignore[arg-type]
    return app.tools


def test_register_with_llm_adds_draft_tool() -> None:
    llm = CannedLLMClient(_VALID_SQL)
    tools = _build_tools(llm=llm)
    assert set(tools.keys()) == {
        "parse_sql_migration",
        "apply_sql_to_sandbox",
        "check_migration_drift",
        "draft_sql_migration_from_intent",
    }


def test_register_without_llm_stub_raises() -> None:
    tools = _build_tools(llm=None)
    handler = tools["draft_sql_migration_from_intent"]
    try:
        handler(intent_text="x", dialect="sqlite")  # type: ignore[operator]
    except RuntimeError as exc:
        assert "PICKLED_DATA_LLM_FACTORY" in str(exc)
    else:
        raise AssertionError("expected RuntimeError when llm is None")
