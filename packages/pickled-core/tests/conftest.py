"""Shared pytest configuration for pickled-core."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "requires_anthropic: needs the anthropic package installed",
    )
    config.addinivalue_line(
        "markers",
        "requires_openai: needs the openai package installed",
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
            if item.name == "test_make_anthropic":
                item.add_marker(skip)

    try:
        import openai  # noqa: F401
    except ImportError:
        skip = pytest.mark.skip(reason="openai package not installed")
        for item in items:
            if item.name == "test_openai_compat_optional_key":
                item.add_marker(skip)

    try:
        from google import genai  # noqa: F401
    except ImportError:
        skip = pytest.mark.skip(reason="google-genai package not installed")
        for item in items:
            if "gemini" in item.nodeid:
                item.add_marker(skip)
