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


@pytest.mark.parametrize(
    "host",
    [
        "::",
        "[::]",
        "0:0:0:0:0:0:0:0",
        "::ffff:0.0.0.0",
        "  0.0.0.0  ",
        " :: ",
    ],
)
def test_refuse_ipv6_and_padded_wildcards_without_flag(host: str) -> None:
    """Any IPv4/IPv6 wildcard ('unspecified') host must require --allow-public.

    The previous guard only blocked the literal ``0.0.0.0``; binding to ``::``
    silently exposed the MCP server on every IPv6 interface, defeating the
    intent of the safety check.
    """
    with pytest.raises(RuntimeError, match="wildcard"):
        resolve_transport("http", host, None, False)


@pytest.mark.parametrize(
    "host",
    ["::", "[::]", "::ffff:0.0.0.0"],
)
def test_allow_ipv6_wildcards_with_flag(host: str) -> None:
    kw = resolve_transport("http", host, 7802, True)
    assert kw["host"] == host
    assert kw["port"] == 7802


@pytest.mark.parametrize(
    "host",
    ["127.0.0.1", "::1", "[::1]", "localhost", "192.168.1.10", "::ffff:127.0.0.1"],
)
def test_allow_loopback_and_specific_hosts_without_flag(host: str) -> None:
    """Loopback addresses and specific hostnames must not be misidentified as wildcards."""
    kw = resolve_transport("http", host, None, False)
    assert kw["host"] == host


@pytest.mark.parametrize(
    "host",
    ["0", "0.0", "0.0.0", "0x0", "00000000", "0.00.0.0", " 0 ", "0x00000000"],
)
def test_refuse_inet_aton_short_forms_without_flag(host: str) -> None:
    """``inet_aton``-style short forms of 0.0.0.0 must also require --allow-public.

    POSIX ``socket.bind(("0", port))``, ``("0.0", port)`` etc. silently
    canonicalise to ``0.0.0.0`` — the very bypass we are guarding against.
    """
    with pytest.raises(RuntimeError, match="wildcard"):
        resolve_transport("http", host, None, False)


@pytest.mark.parametrize(
    "host",
    ["1", "127", "127.1", "10.0.0.1", "0.0.0.1", "0.1.0.0"],
)
def test_allow_inet_aton_specific_addresses_without_flag(host: str) -> None:
    """``inet_aton``-style short forms that resolve to a *specific* address are fine."""
    kw = resolve_transport("http", host, None, False)
    assert kw["host"] == host


def test_hostnames_with_zero_letters_are_not_wildcards() -> None:
    """A hostname like 'zero.example.com' must not be misclassified as a wildcard."""
    kw = resolve_transport("http", "zero.example.com", None, False)
    assert kw["host"] == "zero.example.com"
