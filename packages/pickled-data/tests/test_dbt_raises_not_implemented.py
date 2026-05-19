from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner
from pickled_data.cli import main
from pickled_data.types import DBT_NOT_IMPLEMENTED_MSG


def test_dbt_extension_raises(tmp_path: Path) -> None:
    model = tmp_path / "model.dbt"
    model.write_text("SELECT 1", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["parse", str(model)])
    assert result.exit_code != 0
    msg = result.exception.args[0] if result.exception else result.output
    assert DBT_NOT_IMPLEMENTED_MSG in msg
