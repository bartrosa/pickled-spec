"""Stdio transport reserves stdout for JSON-RPC framing.

Per https://modelcontextprotocol.io/specification/2025-06-18/basic/transports:
"The server MUST NOT write anything to its stdout that is not a valid MCP
message. The server MAY write UTF-8 strings to its standard error (stderr)
for logging purposes."

This module routes all Python logging to stderr before the MCP server
takes over stdout.
"""

from __future__ import annotations

import logging
import sys


def setup_logging_for_stdio(level: int = logging.INFO) -> None:
    """Reconfigure the root logger to write to stderr only. Safe to call twice."""
    logging.basicConfig(
        stream=sys.stderr,
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
        force=True,
    )


__all__ = ["setup_logging_for_stdio"]
