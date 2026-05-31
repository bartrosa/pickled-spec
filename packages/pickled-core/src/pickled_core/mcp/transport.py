"""Resolve CLI transport flags to FastMCP ``run()`` keyword arguments."""

from __future__ import annotations

import ipaddress
import socket
from typing import Any, Literal


def _is_unspecified_address(host: str) -> bool:
    """Return True iff ``host`` is an IPv4/IPv6 wildcard ("unspecified") address.

    The original guard rejected only the literal string ``0.0.0.0``. PR #27
    extended it to cover the IPv6 wildcard (``::`` / ``[::]`` and friends).
    Both are still bypassed by ``inet_aton``-style legacy IPv4 short forms:
    ``socket.bind(("0", port))``, ``("0.0", port)``, ``("0.0.0", port)``,
    ``("0x0", port)`` and ``("00000000", port)`` all silently resolve to
    ``0.0.0.0`` on POSIX systems (and uvicorn / asyncio happily forward them
    to ``socket.bind``). On a host with a public network interface, any of
    these would expose the MCP server without the user passing
    ``--allow-public``.

    We accept the bracketed form ``[::]`` (uvicorn / FastMCP take it as well),
    fully-expanded forms such as ``0:0:0:0:0:0:0:0``, the IPv4-mapped
    wildcard ``::ffff:0.0.0.0``, and any ``inet_aton``-compatible string that
    canonicalises to ``0.0.0.0``. Whitespace is stripped so the heuristic is
    not defeated by trivial copy-paste artifacts. Hostnames are intentionally
    left untouched — we deliberately do not resolve DNS in this guard.
    """
    stripped = host.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        stripped = stripped[1:-1]
    try:
        addr = ipaddress.ip_address(stripped)
    except ValueError:
        addr = None
    if addr is not None:
        if addr.is_unspecified:
            return True
        if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped is not None:
            return addr.ipv4_mapped.is_unspecified
        return False
    if not stripped or any(ch.isspace() for ch in stripped):
        return False
    try:
        packed = socket.inet_aton(stripped)
    except OSError:
        return False
    return packed == b"\x00\x00\x00\x00"


def resolve_transport(
    name: Literal["stdio", "http"],
    host: str | None,
    port: int | None,
    allow_public: bool,
) -> dict[str, Any]:
    """Map user-facing transport name to FastMCP transport kwargs."""
    if name == "stdio":
        return {"transport": "stdio"}
    if name == "http":
        actual_host = host or "127.0.0.1"
        if _is_unspecified_address(actual_host) and not allow_public:
            raise RuntimeError(
                f"refusing to bind wildcard address {actual_host!r} without "
                "--allow-public (irreversible network exposure)"
            )
        return {
            "transport": "streamable-http",
            "host": actual_host,
            "port": port or 7801,
        }
    raise ValueError(f"unknown transport {name!r}")


__all__ = ["resolve_transport"]
