"""Resolve CLI transport flags to FastMCP ``run()`` keyword arguments."""

from __future__ import annotations

from typing import Any, Literal


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
        if actual_host == "0.0.0.0" and not allow_public:
            raise RuntimeError(
                "refusing to bind 0.0.0.0 without --allow-public (irreversible network exposure)"
            )
        return {
            "transport": "streamable-http",
            "host": actual_host,
            "port": port or 7801,
        }
    raise ValueError(f"unknown transport {name!r}")


__all__ = ["resolve_transport"]
