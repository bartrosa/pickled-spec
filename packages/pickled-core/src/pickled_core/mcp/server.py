"""MCP server entry point (re-exports :class:`PickledMCPServer`)."""

from __future__ import annotations

from pickled_core.mcp.runtime import PickledMCPServer

__all__ = ["PickledMCPServer"]
