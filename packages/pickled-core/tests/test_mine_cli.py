"""Tests for pickled-spec mine CLI."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner
from pickled_core.cli import main

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tiny_target"


def test_mine_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["mine", "--help"])
    assert result.exit_code == 0
    for name in ("inventory", "stories", "features", "tag", "evaluate", "report", "all"):
        assert name in result.output


def test_mine_inventory_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["mine", "inventory", "--help"])
    assert result.exit_code == 0
    assert "--output" in result.output
    assert "--no-mcp" in result.output


def test_mine_inventory_cli(tmp_path: Path) -> None:
    runner = CliRunner()
    out = tmp_path / "out"
    result = runner.invoke(
        main,
        [
            "mine",
            "inventory",
            str(_FIXTURE),
            "--output",
            str(out),
            "--no-mcp",
        ],
    )
    assert result.exit_code == 0, result.output
    assert (out / "inventory.json").is_file()


def test_mine_all_phase8a(tmp_path: Path) -> None:
    runner = CliRunner()
    out = tmp_path / "full"
    result = runner.invoke(
        main,
        ["mine", "all", str(_FIXTURE), "--output", str(out), "--no-mcp"],
    )
    assert result.exit_code == 0, result.output
    assert (out / "inventory.json").is_file()
    assert (out / "mining-report.md").is_file()
