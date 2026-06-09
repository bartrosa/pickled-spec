"""Regression tests for the binary-name vs format-label split.

Historically :func:`iac_binary` returned ``"opentofu"`` when only ``tofu``
was on ``PATH``; that string was then handed straight to
:func:`subprocess.run`, which raised
``FileNotFoundError: [Errno 2] No such file or directory: 'opentofu'``
because the OpenTofu CLI ships as ``tofu``, never ``opentofu``. Every
``pickled-iac draft`` invocation and every ``validate_terraform_dir`` MCP
call was broken on OpenTofu-only hosts. The two concerns must stay split:
``iac_binary()`` returns the *executable* name; ``iac_format()`` returns the
human-facing *format label*.

These tests deliberately do not require ``terraform`` or ``tofu`` to be on
``PATH``; they exercise the resolution logic in isolation via patching.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pickled_iac.oracle as oracle_mod
import pytest
from pickled_iac.oracle import iac_binary, iac_format, validate
from pickled_iac.types import IaCToolMissingError


def test_iac_binary_returns_tofu_when_only_tofu_installed() -> None:
    with patch.object(oracle_mod, "_IAC_BIN", "tofu"):
        assert iac_binary() == "tofu"
        assert iac_format() == "opentofu"


def test_iac_binary_returns_terraform_when_terraform_installed() -> None:
    with patch.object(oracle_mod, "_IAC_BIN", "terraform"):
        assert iac_binary() == "terraform"
        assert iac_format() == "terraform"


def test_iac_binary_raises_when_neither_installed() -> None:
    with patch.object(oracle_mod, "_IAC_BIN", None), pytest.raises(IaCToolMissingError):
        iac_binary()


def test_validate_uses_tofu_executable_not_opentofu(tmp_path: Path) -> None:
    """End-to-end: validate() must spawn ``tofu`` (not ``opentofu``) on tofu hosts."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_tofu = bin_dir / "tofu"
    fake_tofu.write_text(
        f"#!{sys.executable}\n"
        "import sys\n"
        "if len(sys.argv) > 1 and sys.argv[1] == 'validate':\n"
        "    print('{\"valid\": true, \"diagnostics\": []}')\n"
        "sys.exit(0)\n",
        encoding="utf-8",
    )
    fake_tofu.chmod(0o755)

    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    (cfg_dir / "main.tf").write_text("# empty\n", encoding="utf-8")

    # Prepend our fake bin dir so PATH lookup hits ``tofu`` first, but keep the
    # standard PATH segments so the python shebang resolves.
    new_path = f"{bin_dir}:{Path(sys.executable).parent}:/usr/bin:/bin"

    with (
        patch.object(oracle_mod, "_IAC_BIN", "tofu"),
        patch.dict("os.environ", {"PATH": new_path}, clear=False),
    ):
        # Sanity-check the failure mode the fix prevents: subprocess.run on the
        # bogus name "opentofu" must raise FileNotFoundError (no such binary).
        with pytest.raises(FileNotFoundError):
            subprocess.run(["opentofu", "validate"], check=False)  # noqa: S603,S607

        result = validate(cfg_dir)
        assert result.valid is True
        assert result.format == "opentofu"


def test_oracle_module_uses_tofu_as_actual_binary_name() -> None:
    """``_IAC_BIN`` must hold the executable name, not the format label.

    Source-level guard so a future refactor cannot silently re-introduce the
    ``opentofu``-as-binary bug while leaving the runtime branch unreached on
    terraform-only CI.
    """
    src = Path(oracle_mod.__file__).read_text(encoding="utf-8")
    assert '_IAC_BIN = "tofu"' in src, "OpenTofu binary must be referenced as 'tofu'"
    assert '_IAC_BIN = "opentofu"' not in src, (
        "Found stale '_IAC_BIN = \"opentofu\"' assignment — subprocess.run "
        "would raise FileNotFoundError because no 'opentofu' executable exists "
        "(OpenTofu installs as 'tofu')."
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
