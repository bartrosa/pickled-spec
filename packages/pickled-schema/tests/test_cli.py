from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

openapi_spec_validator = pytest.importorskip("openapi_spec_validator")

from pickled_schema.cli import main  # noqa: E402


def test_cli_parse_openapi(openapi_fixture: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["parse", str(openapi_fixture)])
    assert result.exit_code == 0
    assert "openapi_3_1" in result.output


def test_cli_validate_openapi(openapi_fixture: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["validate", str(openapi_fixture)])
    assert result.exit_code == 0
    assert '"valid": true' in result.output


def test_cli_check_coverage(openapi_fixture: Path, tmp_path: Path) -> None:
    features = tmp_path / "features"
    features.mkdir()
    (features / "u.feature").write_text(
        "@schema:endpoint:GET-/users\nScenario: L\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["check", "--spec", str(openapi_fixture), "--feature-dir", str(features)],
    )
    assert result.exit_code == 0
    assert '"verdict": "pass"' in result.output
