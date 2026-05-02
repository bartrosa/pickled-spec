"""MCP server scaffolding.

Each pickled-* package registers its tools with a single `PickledMCPServer`
instance. v0.1 ships the in-memory registry only; the transport (stdio
via the `mcp` SDK) lands in v0.1.1, after the tool surface stabilizes for
two consumer packages.
"""

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
