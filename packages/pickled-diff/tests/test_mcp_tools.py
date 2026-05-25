from __future__ import annotations

import json

import pytest

pytest.importorskip("fastmcp")
from pickled_bdd.testing import CannedLLMClient
from pickled_core import PickledMCPServer, ToolAlreadyRegisteredError
from pickled_diff import mcp_tools
from pickled_diff.runner import CallableRunner


class _FakeApp:
    def __init__(self) -> None:
        self.tools: dict[str, object] = {}

    def tool(self, *, name: str | None = None):  # type: ignore[no-untyped-def]
        def deco(fn):  # type: ignore[no-untyped-def]
            assert name is not None
            self.tools[name] = fn
            return fn

        return deco


_CORPUS_JSON = json.dumps(
    [{"name": "a", "payload": "1"}, {"name": "b", "payload": "2"}]
) + "\n---RATIONALE---\nok\n"


def test_register_adds_one_tool() -> None:
    server = PickledMCPServer("test-diff")
    mcp_tools.register(server)
    names = [t.name for t in server.registry.list()]
    assert names == ["verify_against_oracle"]


def test_verify_handler_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_subprocess(
        command: list[str],
        *,
        name: str = "subprocess",
        timeout_seconds: float = 30.0,
    ) -> CallableRunner:
        _ = (command, timeout_seconds)
        return CallableRunner(lambda s: str(int(s) * 2), name=name)

    monkeypatch.setattr(mcp_tools, "SubprocessRunner", fake_subprocess)
    server = PickledMCPServer("test-diff")
    mcp_tools.register(server)
    tool = server.registry.get("verify_against_oracle")
    out = tool.handler(  # type: ignore[operator]
        oracle_command=["ignored"],
        candidate_command=["ignored"],
        corpus_items=[{"name": "one", "payload": "3"}],
        comparator="exact",
        timeout_seconds=5.0,
    )
    assert set(out.keys()) == {"verdict", "notes", "findings"}
    assert out["verdict"] == "pass"
    assert isinstance(out["findings"], list)


def test_register_twice_raises() -> None:
    server = PickledMCPServer("test-diff")
    mcp_tools.register(server)
    with pytest.raises(ToolAlreadyRegisteredError):
        mcp_tools.register(server)


def test_register_with_llm_adds_draft_tool() -> None:
    llm = CannedLLMClient(_CORPUS_JSON)
    app = _FakeApp()
    mcp_tools.register_with_fastmcp(app, llm=llm)  # type: ignore[arg-type]
    assert set(app.tools.keys()) == {
        "verify_against_oracle",
        "draft_corpus_from_examples",
    }


def test_register_without_llm_stub_tool_raises() -> None:
    app = _FakeApp()
    mcp_tools.register_with_fastmcp(app, llm=None)  # type: ignore[arg-type]
    handler = app.tools["draft_corpus_from_examples"]
    try:
        handler(seed_examples=[], target_size=2)  # type: ignore[operator]
    except RuntimeError as exc:
        assert "PICKLED_DIFF_LLM_FACTORY" in str(exc)
    else:
        raise AssertionError("expected RuntimeError when llm is None")
