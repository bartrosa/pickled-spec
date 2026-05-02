"""Tool registry — the v0.1 surface of pickled-spec's MCP integration.

A `ToolRegistry` maps tool names to handlers and metadata. Consumers
(packages) call `register` during their `register(server)` function. The
registry is independent of any specific transport so it can be tested
exhaustively without spinning up a server.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

ToolHandler = Callable[..., Any]
"""A tool handler. Argument shape is described by the JSON schema in
`RegisteredTool.input_schema`. Return shape is JSON-serializable."""


class ToolAlreadyRegisteredError(ValueError):
    """Raised when a tool name is registered more than once."""


@dataclass(frozen=True)
class RegisteredTool:
    """Metadata + handler for a registered MCP tool."""

    name: str
    description: str
    handler: ToolHandler
    input_schema: dict[str, Any]


class ToolRegistry:
    """In-memory tool registry.

    Not thread-safe. v0.1 assumes single-threaded registration at startup
    and single-threaded dispatch at runtime. If we add concurrency later,
    this class is the choke point.
    """

    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(
        self,
        name: str,
        handler: ToolHandler,
        *,
        description: str,
        input_schema: dict[str, Any],
    ) -> RegisteredTool:
        """Register a tool. Raises if the name is already taken."""
        if name in self._tools:
            raise ToolAlreadyRegisteredError(
                f"Tool {name!r} is already registered"
            )
        tool = RegisteredTool(
            name=name,
            description=description,
            handler=handler,
            input_schema=input_schema,
        )
        self._tools[name] = tool
        return tool

    def get(self, name: str) -> RegisteredTool:
        """Look up a tool by name. Raises KeyError if missing."""
        return self._tools[name]

    def list(self) -> list[RegisteredTool]:
        """Return all registered tools, sorted by name."""
        return sorted(self._tools.values(), key=lambda t: t.name)

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._tools
