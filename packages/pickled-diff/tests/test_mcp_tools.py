from __future__ import annotations

import pytest

pytest.importorskip("fastmcp")
from pickled_core import PickledMCPServer, ToolAlreadyRegisteredError
from pickled_diff import mcp_tools
from pickled_diff.runner import CallableRunner


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
