"""Tests for umbrella MCP script discovery in monorepos."""

from __future__ import annotations

from pathlib import Path

from pickled_core.mine.inventory_lib import discover_umbrella_mcp_launch

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tiny_target"


def test_detects_umbrella_script_on_root_pyproject(tmp_path: Path) -> None:
    root_toml = tmp_path / "pyproject.toml"
    root_toml.write_text(
        """
[project]
name = "root-app"
version = "0.0.1"
dependencies = ["click>=8.1"]

[project.scripts]
pickled-spec = "root_app.cli:main"

[project.entry-points."pickled.mcp.subservers"]
bdd = "root_app.mcp:build_server"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    launch = discover_umbrella_mcp_launch(tmp_path)
    assert launch is not None
    script_name, run_dir = launch
    assert script_name == "pickled-spec"
    assert run_dir == tmp_path.resolve()


def test_detects_umbrella_script_on_workspace_member() -> None:
    launch = discover_umbrella_mcp_launch(_FIXTURE)
    assert launch is not None
    script_name, run_dir = launch
    assert script_name == "pickled-spec"
    assert run_dir == _FIXTURE.resolve()


def test_no_umbrella_script_records_warning_not_error(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "plain"
version = "0.0.1"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    assert discover_umbrella_mcp_launch(tmp_path) is None

    from pickled_core.mine.inventory_stage import run_inventory

    out = tmp_path / "out"
    result = run_inventory(tmp_path, out, include_mcp=True, verbose=False)
    assert result.data["totals"]["mcp_tools"] == 0
    assert any("umbrella MCP" in w for w in result.warnings)
