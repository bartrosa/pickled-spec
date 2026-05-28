"""Read/write helpers for mining output directories."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pickled_core.mine.errors import MissingStageInputError
from pickled_core.mine.types import MiningPaths


def parse_surfaces_filter(raw: str | None) -> tuple[str, ...]:
    """Parse comma-separated ``--surfaces`` tokens (lowercased)."""
    if not raw or not raw.strip():
        return ()
    return tuple(token.strip().lower() for token in raw.split(",") if token.strip())


def surface_matches(
    *,
    surface_id: str,
    package: str,
    tokens: tuple[str, ...],
) -> bool:
    """Return True when no filter or any token matches package or surface-id."""
    if not tokens:
        return True
    pkg = package.lower()
    sid = surface_id.lower()
    return any(token in pkg or token in sid for token in tokens)


def ensure_output_dir(output_dir: Path) -> MiningPaths:
    """Create the mining output tree if missing."""
    paths = MiningPaths(output_dir.resolve())
    paths.root.mkdir(parents=True, exist_ok=True)
    paths.stories_dir.mkdir(parents=True, exist_ok=True)
    paths.features_dir.mkdir(parents=True, exist_ok=True)
    paths.evaluation_dir.mkdir(parents=True, exist_ok=True)
    paths.runs_dir.mkdir(parents=True, exist_ok=True)
    return paths


def read_json(path: Path) -> Any:
    if not path.is_file():
        msg = f"required input missing: {path}"
        raise FileNotFoundError(msg)
    return json.loads(path.read_text(encoding="utf-8"))


def require_inventory_json(
    output_dir: Path,
    *,
    needed_by: str = "stories",
) -> Any:
    """Load ``inventory.json`` or raise :class:`MissingStageInputError`."""
    paths = ensure_output_dir(output_dir)
    if not paths.inventory_json.is_file():
        raise MissingStageInputError(
            paths.inventory_json,
            needed_by=needed_by,
            produced_by="inventory",
        )
    return read_json(paths.inventory_json)


def require_stories_dir(
    output_dir: Path,
    *,
    needed_by: str = "features",
) -> Path:
    """Return stories directory or raise :class:`MissingStageInputError`."""
    paths = ensure_output_dir(output_dir)
    if not paths.stories_dir.is_dir():
        raise MissingStageInputError(
            paths.stories_dir,
            needed_by=needed_by,
            produced_by="stories",
        )
    stories = sorted(paths.stories_dir.glob("*.story.md"))
    if not stories:
        raise MissingStageInputError(
            paths.stories_dir,
            needed_by=needed_by,
            produced_by="stories",
        )
    return paths.stories_dir


def require_features_dir(
    output_dir: Path,
    *,
    needed_by: str = "tag",
) -> Path:
    """Return features directory or raise :class:`MissingStageInputError`."""
    paths = ensure_output_dir(output_dir)
    if not paths.features_dir.is_dir():
        raise MissingStageInputError(
            paths.features_dir,
            needed_by=needed_by,
            produced_by="features",
        )
    features = sorted(paths.features_dir.glob("*.feature"))
    if not features:
        raise MissingStageInputError(
            paths.features_dir,
            needed_by=needed_by,
            produced_by="features",
        )
    return paths.features_dir


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json_optional(path: Path) -> Any | None:
    if not path.is_file():
        return None
    return read_json(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


__all__ = [
    "ensure_output_dir",
    "parse_surfaces_filter",
    "read_json",
    "read_json_optional",
    "require_features_dir",
    "require_inventory_json",
    "require_stories_dir",
    "surface_matches",
    "write_json",
    "write_text",
]
