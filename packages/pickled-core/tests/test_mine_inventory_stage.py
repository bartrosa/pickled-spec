"""Tests for mine inventory stage."""

from __future__ import annotations

from pathlib import Path

from pickled_core.mine.inventory_stage import run_inventory

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tiny_target"


def test_run_inventory_tiny_target(tmp_path: Path) -> None:
    result = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    assert result.inventory_path.is_file()
    data = result.data
    assert data["totals"]["cli_commands"] >= 2
    assert "tiny-target" in data["packages"]
    commands = data["packages"]["tiny-target"]["cli_commands"]
    names = {c["full_name"] for c in commands}
    assert "greet" in names
    assert "ping" in names


def test_inventory_skips_mcp_without_pickled_spec(tmp_path: Path) -> None:
    result = run_inventory(_FIXTURE, tmp_path, include_mcp=True, verbose=False)
    mcp_ok = result.data["totals"]["mcp_tools"] == 0
    assert any("pickled-spec" in w for w in result.warnings) or mcp_ok
