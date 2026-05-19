"""Regression test: ``validate_files`` must reject path-traversal filenames.

Caller-supplied filenames flow through to disk via the
``validate_terraform_dir`` MCP tool, which calls
:func:`pickled_iac.oracle.validate_files`. Before the fix a filename like
``../../etc/foo`` would be written outside the temp directory, allowing
arbitrary-file-write by any MCP client. These tests lock in the rejection.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pickled_iac.oracle import (
    UnsafeTerraformFilenameError,
    _safe_join,
    validate_files,
)


@pytest.mark.parametrize(
    "bad_name",
    [
        "../escape.tf",
        "../../etc/passwd",
        "subdir/../../escape.tf",
        "/absolute/path.tf",
        "main.tf\x00.evil",
        "",
    ],
)
def test_validate_files_rejects_unsafe_filename(bad_name: str) -> None:
    with pytest.raises(UnsafeTerraformFilenameError):
        validate_files({bad_name: 'resource "null_resource" "x" {}'})


def test_safe_join_allows_nested_relative_path(tmp_path: Path) -> None:
    target = _safe_join(tmp_path, "modules/net/main.tf")
    assert target.parent == (tmp_path / "modules" / "net").resolve()
    assert target.name == "main.tf"


def test_safe_join_rejects_traversal(tmp_path: Path) -> None:
    with pytest.raises(UnsafeTerraformFilenameError):
        _safe_join(tmp_path, "../escape.tf")


def test_safe_join_rejects_absolute(tmp_path: Path) -> None:
    with pytest.raises(UnsafeTerraformFilenameError):
        _safe_join(tmp_path, "/tmp/escape.tf")


def test_validate_files_does_not_write_outside_tempdir(tmp_path: Path) -> None:
    sentinel = tmp_path / "sentinel.txt"
    relative_escape = f"../{sentinel.name}"
    # Resolve from a child path so the relative escape would (without the fix)
    # write into ``tmp_path``. We're not asserting any file is written; we're
    # asserting that ``validate_files`` refuses the request entirely.
    with pytest.raises(UnsafeTerraformFilenameError):
        validate_files({relative_escape: "should not be written"})
    assert not sentinel.exists()
