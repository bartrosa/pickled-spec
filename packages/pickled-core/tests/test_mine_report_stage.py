"""Tests for mine report stage."""

from __future__ import annotations

from pathlib import Path

from pickled_core.mine.inventory_stage import run_inventory
from pickled_core.mine.report_stage import render_mining_report, run_report

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tiny_target"


def test_report_mentions_cli_commands(tmp_path: Path) -> None:
    run_inventory(_FIXTURE, tmp_path, include_mcp=False)
    report_path = run_report(tmp_path, target_label=str(_FIXTURE))
    text = report_path.read_text(encoding="utf-8")
    assert "greet" in text or "CLI commands" in text
    assert "tiny-target" in text


def test_render_handles_inventory_only(tmp_path: Path) -> None:
    run_inventory(_FIXTURE, tmp_path, include_mcp=False)
    md = render_mining_report(tmp_path)
    assert "## Summary" in md
    assert "## Inventory highlights" in md
