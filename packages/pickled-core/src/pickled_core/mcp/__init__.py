"""MCP server scaffolding (FastMCP transport + umbrella composition)."""

from pickled_core.mcp.registry import (
    RegisteredTool,
    ToolAlreadyRegisteredError,
    ToolHandler,
    ToolRegistry,
)
from pickled_core.mcp.server import PickledMCPServer

__all__ = [
    "PickledMCPServer",
    "RegisteredTool",
    "ToolAlreadyRegisteredError",
    "ToolHandler",
    "ToolRegistry",
]
