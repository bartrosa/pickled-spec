from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from pickled_iac.oracle import validate

pytestmark = pytest.mark.skipif(
    not shutil.which("terraform") and not shutil.which("tofu"),
    reason="terraform or tofu not on PATH",
)


def test_validate_users_rds_happy_path(users_rds_dir: Path) -> None:
    result = validate(users_rds_dir)
    assert result.valid is True
    assert result.diagnostics == []


def test_validate_syntax_error(tmp_path: Path) -> None:
    bad = tmp_path / "main.tf"
    bad.write_text('resource "aws_s3_bucket" "x" {', encoding="utf-8")
    result = validate(tmp_path)
    assert result.valid is False
    assert result.diagnostics
