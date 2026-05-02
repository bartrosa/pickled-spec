from __future__ import annotations

import pytest
from pickled_bdd import mcp_tools
from pickled_bdd.testing import CannedLLMClient
from pickled_core import PickledMCPServer, ToolAlreadyRegisteredError


def test_register_adds_two_tools() -> None:
    llm = CannedLLMClient(
        '{"is_ambiguous": false, "alternatives": [], "suggested_fix": ""}'
    )
    server = PickledMCPServer()
    mcp_tools.register(server, llm=llm)
    names = [t.name for t in server.registry.list()]
    assert names == [
        "draft_feature_from_story",
        "validate_feature_ambiguity",
    ]


def test_draft_handler_shape() -> None:
    feature_body = "Feature: X\n  Scenario: Y\n    Given z\n"
    llm = CannedLLMClient(feature_body)
    server = PickledMCPServer()
    mcp_tools.register(server, llm=llm)

    tool = server.registry.get("draft_feature_from_story")
    out = tool.handler(story_text="As a user I want X")  # type: ignore[operator]

    assert set(out.keys()) == {"feature_text", "rationale", "warnings"}
    assert out["feature_text"] == feature_body.strip()
    assert isinstance(out["warnings"], list)


def test_validate_handler_shape() -> None:
    ok = '{"is_ambiguous": false, "alternatives": [], "suggested_fix": ""}'
    llm = CannedLLMClient(ok)
    server = PickledMCPServer()
    mcp_tools.register(server, llm=llm)

    gherkin = """Feature: Smoke
  Scenario: One
    Given x
"""
    tool = server.registry.get("validate_feature_ambiguity")
    out = tool.handler(feature_text=gherkin)  # type: ignore[operator]

    assert set(out.keys()) == {"verdict", "notes", "findings"}
    assert out["verdict"] == "pass"
    assert isinstance(out["findings"], list)


def test_register_twice_raises() -> None:
    llm = CannedLLMClient("x")
    server = PickledMCPServer()
    mcp_tools.register(server, llm=llm)
    with pytest.raises(ToolAlreadyRegisteredError):
        mcp_tools.register(server, llm=llm)
