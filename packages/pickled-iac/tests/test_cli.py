from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner
from pickled_iac.cli import main


def test_cli_diff_pass(empty_plan: dict, tmp_path: Path) -> None:
    base = tmp_path / "base.json"
    head = tmp_path / "head.json"
    base.write_text(json.dumps(empty_plan), encoding="utf-8")
    head.write_text(json.dumps(empty_plan), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["diff", "--base", str(base), "--head", str(head)])
    assert result.exit_code == 0


@pytest.mark.skipif(
    not shutil.which("terraform") and not shutil.which("tofu"),
    reason="terraform not on PATH",
)
def test_cli_validate(users_rds_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["validate", str(users_rds_dir)])
    assert result.exit_code == 0
    assert '"valid": true' in result.output
