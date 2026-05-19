"""FastMCP-backed :class:`PickledMCPServer` implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal, cast

if TYPE_CHECKING:
    from fastmcp import FastMCP

from pickled_core.mcp.registry import ToolHandler, ToolRegistry

logger = logging.getLogger(__name__)


class PickledMCPServer:
    """Central MCP server for the pickled-* family.

    Holds an in-memory :class:`ToolRegistry` and mirrors registrations onto a
    FastMCP application for stdio or streamable HTTP transport.
    """

    def __init__(self, name: str = "pickled") -> None:
        from fastmcp import FastMCP

        from pickled_core.mcp.resources import register_core_resources

        self._registry = ToolRegistry()
        self._app = FastMCP(name)
        register_core_resources(self)

    @property
    def registry(self) -> ToolRegistry:
        return self._registry

    @property
    def fastmcp_app(self) -> FastMCP:
        """Underlying FastMCP instance for composition (umbrella mount)."""
        return self._app

    def register_tool(
        self,
        name: str,
        handler: ToolHandler,
        *,
        description: str,
        input_schema: dict[str, Any],
    ) -> None:
        """Register a tool on the registry and expose it via FastMCP."""
        tool = self._registry.register(
            name,
            handler,
            description=description,
            input_schema=input_schema,
        )
        self._bind_fastmcp_tool(tool)

    def _bind_fastmcp_tool(self, tool: Any) -> None:
        """Wire a :class:`RegisteredTool` onto the FastMCP app."""
        self._app.tool(name=tool.name, description=tool.description)(tool.handler)

    def serve(
        self,
        transport: Literal["stdio", "streamable-http"] = "stdio",
        **kwargs: Any,
    ) -> None:
        """Start serving over stdio or streamable HTTP."""
        from pickled_core.mcp.stdio_logging import setup_logging_for_stdio

        if transport == "stdio":
            setup_logging_for_stdio()
        logger.info("starting MCP server transport=%s", transport)
        self._app.run(transport=cast(Any, transport), **kwargs)


__all__ = ["PickledMCPServer"]
