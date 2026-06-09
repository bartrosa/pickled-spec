"""Subprocess wrappers for Terraform / OpenTofu validate and plan."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Literal

from pickled_iac.types import IaCToolMissingError, PlanResult, ValidateResult

# The executable name to invoke via subprocess. OpenTofu's binary is ``tofu``
# (see https://opentofu.org/docs/intro/install/); ``opentofu`` is the format
# label only, never an installed binary, so we MUST keep these two separate
# or every drafter / validate / plan call fails with FileNotFoundError on
# OpenTofu-only hosts.
_IAC_BIN: Literal["terraform", "tofu"] | None
if shutil.which("terraform"):
    _IAC_BIN = "terraform"
elif shutil.which("tofu"):
    _IAC_BIN = "tofu"
else:
    _IAC_BIN = None


def iac_binary() -> Literal["terraform", "tofu"]:
    """Return the IaC CLI executable name to pass to :func:`subprocess.run`."""
    if _IAC_BIN is None:
        raise IaCToolMissingError(
            "neither 'terraform' nor 'tofu' found on PATH; "
            "install Terraform >=1.7.5 or OpenTofu >=1.8"
        )
    return _IAC_BIN


def iac_format() -> Literal["terraform", "opentofu"]:
    """Return the human-facing format label (``terraform`` or ``opentofu``)."""
    return "opentofu" if iac_binary() == "tofu" else "terraform"


def _run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "TF_IN_AUTOMATION": "1"},
    )


def _init_if_needed(tf_dir: Path, binary: Literal["terraform", "tofu"]) -> None:
    if (tf_dir / ".terraform").exists():
        return
    init = _run([binary, "init", "-input=false", "-backend=false"], cwd=tf_dir)
    if init.returncode != 0:
        err = (init.stderr or init.stdout or "terraform init failed").strip()
        msg = f"{binary} init failed: {err}"
        raise RuntimeError(msg)


def validate(tf_dir: Path) -> ValidateResult:
    """Run ``terraform validate -json`` (or OpenTofu equivalent)."""
    binary = iac_binary()
    _init_if_needed(tf_dir, binary)
    proc = _run([binary, "validate", "-json"], cwd=tf_dir)
    fmt = iac_format()
    if proc.returncode != 0 and not proc.stdout.strip():
        err = (proc.stderr or "validate failed").strip()
        return ValidateResult(valid=False, diagnostics=[err], format=fmt)
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        err = (proc.stderr or proc.stdout or "invalid validate JSON").strip()
        return ValidateResult(valid=False, diagnostics=[err], format=fmt)
    valid = bool(payload.get("valid"))
    diags: list[str] = []
    for d in payload.get("diagnostics", []):
        if isinstance(d, dict):
            summary = d.get("summary") or d.get("detail") or str(d)
            diags.append(str(summary))
    return ValidateResult(valid=valid, diagnostics=diags, format=fmt)


def plan(tf_dir: Path, out_file: Path) -> PlanResult:
    """Run plan and return parsed JSON from ``terraform show -json``."""
    binary = iac_binary()
    _init_if_needed(tf_dir, binary)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plan_proc = _run(
        [binary, "plan", f"-out={out_file.name}", "-input=false", "-no-color"],
        cwd=tf_dir,
    )
    if plan_proc.returncode != 0:
        err = (plan_proc.stderr or plan_proc.stdout or "plan failed").strip()
        msg = f"{binary} plan failed: {err}"
        raise RuntimeError(msg)
    show_proc = _run([binary, "show", "-json", out_file.name], cwd=tf_dir)
    if show_proc.returncode != 0:
        err = (show_proc.stderr or show_proc.stdout or "show failed").strip()
        msg = f"{binary} show failed: {err}"
        raise RuntimeError(msg)
    plan_json = json.loads(show_proc.stdout or "{}")
    fmt = iac_format()
    return PlanResult(plan_json=plan_json, plan_file=out_file, format=fmt)


class UnsafeTerraformFilenameError(ValueError):
    """Raised when ``validate_files`` is given a filename that would escape the temp dir."""


def _safe_join(root: Path, name: str) -> Path:
    """Resolve ``root / name`` while refusing path traversal or absolute paths.

    Caller-supplied filenames (e.g. from an MCP tool request) must not be able
    to write outside the temp directory. We:

    * Reject empty names, null bytes, absolute paths, and any path component
      equal to ``..`` (the explicit traversal token).
    * After resolution, require that the candidate path is still inside
      ``root`` to defend against tricks such as symlinked components.
    """
    if not name:
        raise UnsafeTerraformFilenameError("empty filename")
    if "\x00" in name:
        raise UnsafeTerraformFilenameError(f"filename contains NUL byte: {name!r}")
    candidate = Path(name)
    if candidate.is_absolute() or (candidate.drive and candidate.drive != ""):
        raise UnsafeTerraformFilenameError(f"absolute filename not allowed: {name!r}")
    if any(part == ".." for part in candidate.parts):
        raise UnsafeTerraformFilenameError(f"filename must not contain '..': {name!r}")
    root_resolved = root.resolve()
    target = (root_resolved / candidate).resolve()
    try:
        target.relative_to(root_resolved)
    except ValueError as exc:
        raise UnsafeTerraformFilenameError(
            f"filename escapes temp dir: {name!r}"
        ) from exc
    return target


def validate_files(tf_files: dict[str, str]) -> ValidateResult:
    """Write *tf_files* to a temp dir and validate.

    Filenames are caller-supplied (notably via the
    ``validate_terraform_dir`` MCP tool) so they are sanitised here to
    prevent path-traversal arbitrary-file-write outside the temp dir.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name, body in tf_files.items():
            target = _safe_join(root, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
        return validate(root)


def plan_json_from_dict(plan_data: dict[str, Any]) -> dict[str, Any]:
    """Return plan JSON as-is (helper for tests and MCP)."""
    return plan_data


__all__ = [
    "UnsafeTerraformFilenameError",
    "iac_binary",
    "iac_format",
    "plan",
    "plan_json_from_dict",
    "validate",
    "validate_files",
]
