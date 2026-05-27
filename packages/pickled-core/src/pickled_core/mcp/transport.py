"""Resolve CLI transport flags to FastMCP ``run()`` keyword arguments."""

from __future__ import annotations

import ipaddress
from typing import Any, Literal


def _is_unspecified_address(host: str) -> bool:
    """Return True iff ``host`` is an IPv4/IPv6 wildcard ("unspecified") address.

    The previous implementation only rejected the literal string ``0.0.0.0``,
    which let callers bind to ``::`` / ``[::]`` (the IPv6 wildcard) and bypass
    the "no public binding without --allow-public" guard. That is a real
    accidental-exposure footgun on any host with a routable IPv6 address: the
    OS happily listens on every IPv6 interface, including public ones, and
    typically accepts IPv4 traffic too via dual-stack mapping.

    We accept the bracketed form ``[::]`` (uvicorn / FastMCP take it as well),
    fully-expanded forms such as ``0:0:0:0:0:0:0:0``, and the IPv4-mapped
    wildcard ``::ffff:0.0.0.0``. Whitespace is stripped so the heuristic is
    not defeated by trivial copy-paste artifacts. Hostnames are intentionally
    left untouched — we deliberately do not resolve DNS in this guard.
    """
    stripped = host.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        stripped = stripped[1:-1]
    try:
        addr = ipaddress.ip_address(stripped)
    except ValueError:
        return False
    if addr.is_unspecified:
        return True
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped is not None:
        return addr.ipv4_mapped.is_unspecified
    return False


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
