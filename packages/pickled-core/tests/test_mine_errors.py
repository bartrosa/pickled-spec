"""Tests for actionable mine pipeline errors."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner
from pickled_core.cli import main
from pickled_core.mine.errors import MissingStageInputError
from pickled_core.mine.io import require_inventory_json

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tiny_target"


def test_missing_inventory_raises_actionable_message(tmp_path: Path) -> None:
    with pytest.raises(MissingStageInputError, match="mine inventory"):
        require_inventory_json(tmp_path, needed_by="stories")


def test_cli_catches_mineerror_no_traceback_exit_2(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "mine",
            "stories",
            str(_FIXTURE),
            "--output",
            str(tmp_path / "empty"),
        ],
    )
    assert result.exit_code == 2
    assert "mine inventory" in result.output
    assert "Traceback" not in result.output
