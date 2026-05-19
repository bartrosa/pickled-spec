"""Shared pytest configuration for pickled-core."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "requires_anthropic: needs the anthropic package installed",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    try:
        import anthropic  # noqa: F401
    except ImportError:
        skip = pytest.mark.skip(reason="anthropic package not installed")
        for item in items:
            if "anthropic" in item.nodeid or item.path.name in {
                "test_llm_anthropic.py",
                "test_llm_client.py",
            }:
                item.add_marker(skip)
