from __future__ import annotations

from click.testing import CliRunner
from pickled_data.cli import main


def test_cli_parse(migration_file) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["parse", str(migration_file)])
    assert result.exit_code == 0
    assert "kind" in result.output


def test_cli_apply(migration_file) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["apply", str(migration_file)])
    assert result.exit_code == 0
    assert "users" in result.output


def test_cli_check_drift(migration_file, expected_users_schema) -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "check-drift",
            "--migration",
            str(migration_file),
            "--expected",
            str(expected_users_schema),
        ],
    )
    assert result.exit_code == 0
