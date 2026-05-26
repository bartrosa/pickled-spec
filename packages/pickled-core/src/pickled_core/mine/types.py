"""Shared types for the mining pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class InventoryResult:
    """Result of the inventory stage."""

    inventory_path: Path
    data: dict[str, Any]
    warnings: list[str] = field(default_factory=list)


@dataclass
class StageResult:
    """Generic stage completion metadata."""

    stage: str
    output_dir: Path
    warnings: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


@dataclass
class MiningPaths:
    """Canonical paths under a mining output directory."""

    root: Path

    @property
    def inventory_json(self) -> Path:
        return self.root / "inventory.json"

    @property
    def stories_dir(self) -> Path:
        return self.root / "stories"

    @property
    def features_dir(self) -> Path:
        return self.root / "features"

    @property
    def tags_proposals(self) -> Path:
        return self.root / "tags-proposals.json"

    @property
    def evaluation_dir(self) -> Path:
        return self.root / "evaluation"

    @property
    def coverage_json(self) -> Path:
        return self.evaluation_dir / "coverage.json"

    @property
    def ambiguity_json(self) -> Path:
        return self.evaluation_dir / "ambiguity.json"

    @property
    def mining_report(self) -> Path:
        return self.root / "mining-report.md"

    @property
    def runs_dir(self) -> Path:
        return self.root / "runs"


__all__ = ["InventoryResult", "MiningPaths", "StageResult"]
