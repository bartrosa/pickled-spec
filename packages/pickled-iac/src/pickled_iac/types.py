"""Domain types for pickled-iac."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True, slots=True)
class IaCArtifact:
    """Terraform / OpenTofu module source held in memory."""

    content: str
    format: Literal["terraform", "opentofu"]
    path: Path | None = None


@dataclass(frozen=True, slots=True)
class ValidateResult:
    valid: bool
    diagnostics: list[str] = field(default_factory=list)
    format: Literal["terraform", "opentofu"] = "terraform"


@dataclass(frozen=True, slots=True)
class PlanResult:
    plan_json: dict[str, Any]
    plan_file: Path | None
    format: Literal["terraform", "opentofu"] = "terraform"


class IaCToolMissingError(RuntimeError):
    """Neither ``terraform`` nor ``tofu`` was found on PATH."""


__all__ = [
    "IaCArtifact",
    "IaCToolMissingError",
    "PlanResult",
    "ValidateResult",
]
