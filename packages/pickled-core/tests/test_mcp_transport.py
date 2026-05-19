from __future__ import annotations

import pytest
from pickled_core.mcp.transport import resolve_transport


def test_stdio_transport() -> None:
    assert resolve_transport("stdio", None, None, False) == {"transport": "stdio"}


def test_http_defaults() -> None:
    kw = resolve_transport("http", None, None, False)
    assert kw["transport"] == "streamable-http"
    assert kw["host"] == "127.0.0.1"
    assert kw["port"] == 7801


def test_refuse_public_bind_without_flag() -> None:
    with pytest.raises(RuntimeError, match="0.0.0.0"):
        resolve_transport("http", "0.0.0.0", 9000, False)


def test_allow_public_bind() -> None:
    kw = resolve_transport("http", "0.0.0.0", 9000, True)
    assert kw["host"] == "0.0.0.0"
    assert kw["port"] == 9000
