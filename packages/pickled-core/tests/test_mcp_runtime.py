from __future__ import annotations

import pytest

fastmcp = pytest.importorskip("fastmcp")

from pickled_core.mcp import PickledMCPServer, ToolAlreadyRegisteredError  # noqa: E402


def stub() -> dict[str, bool]:
    return {"ok": True}


def test_register_tool_exposes_on_fastmcp() -> None:
    server = PickledMCPServer("test-server")
    server.register_tool("ping", stub, description="ping", input_schema={})
    assert "ping" in server.registry
    assert len(server.registry) == 1


def test_duplicate_register_raises() -> None:
    server = PickledMCPServer("dup")
    server.register_tool("x", stub, description="a", input_schema={})
    with pytest.raises(ToolAlreadyRegisteredError):
        server.register_tool("x", stub, description="b", input_schema={})


def test_build_umbrella_discovers_subservers() -> None:
    from pickled_core.mcp.umbrella import build_umbrella

    umbrella = build_umbrella()
    assert umbrella is not None
