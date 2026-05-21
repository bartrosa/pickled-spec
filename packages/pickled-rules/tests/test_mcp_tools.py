"""MCP tool surface tests for pickled-rules.

The dedicated regression test ``test_check_ruleset_coverage_does_not_read_paths``
locks in the fix for the arbitrary-file-read primitive that existed when the
tool accepted ``feature_file_paths`` and forwarded them to
``PytestBddAdapter.parse_feature_file``. The Gherkin parser embeds the
offending file content verbatim into ``CompositeParserException`` messages,
so any non-Gherkin file the server could read leaked in error responses.
"""

from __future__ import annotations

from pathlib import Path

from pickled_rules.mcp_tools import register_with_fastmcp


class _FakeApp:
    """Minimal stand-in for FastMCP capturing decorated tool functions."""

    def __init__(self) -> None:
        self.tools: dict[str, object] = {}

    def tool(self, *, name: str | None = None):  # type: ignore[no-untyped-def]
        def deco(fn):  # type: ignore[no-untyped-def]
            assert name is not None
            self.tools[name] = fn
            return fn

        return deco


_TINY_RULESET_YAML = """
metadata:
  source_id: tiny
  source_title: Tiny
  applies_to: global
  maintainer: tests
  source_version: '1.0'
  active_from: '2025-01-01'
rules:
  - id: r1
    title: One
    description: First.
    enforcement: strict
"""


def _build_tools() -> dict[str, object]:
    app = _FakeApp()
    register_with_fastmcp(app)  # type: ignore[arg-type]
    return app.tools


def test_check_ruleset_coverage_accepts_feature_texts() -> None:
    handler = _build_tools()["check_ruleset_coverage"]
    feature_text = (
        "Feature: T\n"
        "  @tiny:r1\n"
        "  Scenario: S\n"
        "    Given x\n"
    )
    result = handler(  # type: ignore[operator]
        ruleset_yaml_text=_TINY_RULESET_YAML,
        feature_texts=[feature_text],
        ruleset_short_name="tiny",
    )
    assert result["verdict"] == "pass"
    assert result["reports"][0]["feature_index"] == 0
    assert "feature_path" not in result["reports"][0]
    assert result["reports"][0]["referenced_rule_ids"] == ["r1"]


def test_check_ruleset_coverage_rejects_path_argument(tmp_path: Path) -> None:
    """The tool must not accept ``feature_file_paths`` (the old, vulnerable arg).

    Catching this at the call site closes the arbitrary-file-read primitive
    described in the module docstring of ``mcp_tools``: a hostile MCP client
    used to be able to point the tool at e.g. ``/etc/passwd`` and read its
    contents back through Gherkin parser error messages.
    """
    secret = tmp_path / "fake-passwd"
    secret.write_text("root:x:0:0:root:/root:/bin/bash\n", encoding="utf-8")

    handler = _build_tools()["check_ruleset_coverage"]
    try:
        handler(  # type: ignore[operator]
            ruleset_yaml_text=_TINY_RULESET_YAML,
            feature_file_paths=[str(secret)],
            ruleset_short_name="tiny",
        )
    except TypeError as exc:
        assert "feature_file_paths" in str(exc) or "unexpected keyword" in str(exc)
    else:
        raise AssertionError(
            "check_ruleset_coverage must not accept 'feature_file_paths'; "
            "see module docstring for the file-read primitive this would "
            "re-introduce."
        )


def test_check_ruleset_coverage_does_not_read_paths(tmp_path: Path) -> None:
    """A path-shaped string in ``feature_texts`` is parsed as Gherkin text.

    The text is fed straight to the Gherkin parser; no ``read_text`` is
    performed, so secrets on disk cannot leak into the parser exception.
    """
    secret_value = "SECRET_TOKEN=sk_live_should_not_be_read"
    secret = tmp_path / "secret.env"
    secret.write_text(secret_value + "\n", encoding="utf-8")

    handler = _build_tools()["check_ruleset_coverage"]
    raised_message = ""
    try:
        handler(  # type: ignore[operator]
            ruleset_yaml_text=_TINY_RULESET_YAML,
            feature_texts=[str(secret)],
            ruleset_short_name="tiny",
        )
    except Exception as exc:  # noqa: BLE001 — assert the message stays clean
        raised_message = str(exc)

    assert secret_value not in raised_message, (
        "parser exception leaked file content; see module docstring"
    )
