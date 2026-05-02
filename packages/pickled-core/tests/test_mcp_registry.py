from __future__ import annotations

import pytest
from pickled_core.mcp import (
    PickledMCPServer,
    ToolAlreadyRegisteredError,
    ToolRegistry,
)


def stub(**kwargs: object) -> dict[str, bool]:
    _ = kwargs
    return {"ok": True}


def test_registry_starts_empty() -> None:
    reg = ToolRegistry()
    assert len(reg) == 0


def test_register_get_and_contains() -> None:
    reg = ToolRegistry()
    reg.register(
        "draft",
        stub,
        description="Draft a feature",
        input_schema={},
    )
    assert "draft" in reg
    assert len(reg) == 1
    t = reg.get("draft")
    assert t.name == "draft"
    assert t.description == "Draft a feature"
    assert t.input_schema == {}
    assert t.handler(**{}) == {"ok": True}


def test_duplicate_register_raises() -> None:
    reg = ToolRegistry()
    reg.register("draft", stub, description="a", input_schema={})
    with pytest.raises(ToolAlreadyRegisteredError, match="already registered"):
        reg.register("draft", stub, description="b", input_schema={})


def test_list_sorted_by_name() -> None:
    reg = ToolRegistry()
    reg.register("zebra", stub, description="z", input_schema={})
    reg.register("alpha", stub, description="a", input_schema={})
    names = [t.name for t in reg.list()]
    assert names == ["alpha", "zebra"]


def test_pickled_mcp_server_serve_raises() -> None:
    server = PickledMCPServer()
    with pytest.raises(NotImplementedError, match="MCP transport lands in v0\\.1\\.1"):
        server.serve()


def test_register_tool_updates_server_registry() -> None:
    server = PickledMCPServer()
    assert len(server.registry) == 0
    server.register_tool(
        "draft",
        stub,
        description="Draft",
        input_schema={"type": "object"},
    )
    assert len(server.registry) == 1
    assert "draft" in server.registry
    assert server.registry.get("draft").description == "Draft"
