"""MCP server entry point.

v0.1: registry-only. `serve()` raises NotImplementedError to make the gap
explicit. The intent is that consumer packages can call `register_tool`
TODAY and the same call sites will work once transport lands in v0.1.1.
"""

from __future__ import annotations

from typing import Any

from pickled_core.mcp.registry import ToolHandler, ToolRegistry


class PickledMCPServer:
    """Central MCP server for the pickled-* family.

    v0.1 holds tools in an in-memory registry. v0.1.1 will wire the
    `mcp` Python SDK to expose these tools over stdio.
    """

    def __init__(self) -> None:
        self._registry = ToolRegistry()

    @property
    def registry(self) -> ToolRegistry:
        return self._registry

    def register_tool(
        self,
        name: str,
        handler: ToolHandler,
        *,
        description: str,
        input_schema: dict[str, Any],
    ) -> None:
        """Register a tool with this server.

        See `pickled_core.mcp.registry.ToolRegistry.register`.
        """
        self._registry.register(
            name,
            handler,
            description=description,
            input_schema=input_schema,
        )

    def serve(self) -> None:
        """Start serving over a transport.

        Not implemented in v0.1. Consumer packages can still register
        tools; the registration is preserved for the future transport.
        """
        raise NotImplementedError(
            "MCP transport lands in v0.1.1. Tools registered via "
            "`register_tool` are held in the registry and will be "
            "exposed when transport is wired."
        )
